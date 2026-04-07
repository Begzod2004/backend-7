import io
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from openpyxl import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from core.permissions import CanManageInvoices
from .models import ShotInvoice
from .serializers import ShotInvoiceSerializer


class ShotInvoiceViewSet(viewsets.ModelViewSet):
    serializer_class = ShotInvoiceSerializer
    permission_classes = [CanManageInvoices]
    filterset_fields = ['warehouse', 'status', 'batch']
    search_fields = ['invoice_number', 'supplier_name', 'document_number']
    ordering_fields = ['created_at', 'document_date', 'total_amount']

    def get_queryset(self):
        return ShotInvoice.objects.select_related(
            'batch', 'warehouse', 'created_by'
        ).all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'], url_path='pdf')
    def download_pdf(self, request, pk=None):
        invoice = self.get_object()
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph(f"Shot Faktura: {invoice.invoice_number}", styles['Title']))
        elements.append(Spacer(1, 0.5 * cm))

        data = [
            ["Ma'lumot", "Qiymat"],
            ["Faktura raqami", invoice.invoice_number],
            ["Partiya", invoice.batch.batch_number],
            ["Ombor", invoice.warehouse.name],
            ["Yetkazib beruvchi", invoice.supplier_name],
            ["Hujjat raqami", invoice.document_number],
            ["Hujjat sanasi", str(invoice.document_date)],
            ["Miqdor", str(invoice.quantity)],
            ["Narx", f"{invoice.price:,.2f}"],
            ["Umumiy summa", f"{invoice.total_amount:,.2f}"],
            ["Holat", invoice.get_status_display()],
            ["Izoh", invoice.note or "-"],
        ]

        table = Table(data, colWidths=[7 * cm, 10 * cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        elements.append(table)
        doc.build(elements)

        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
        return response

    @action(detail=False, methods=['get'], url_path='export')
    def export_excel(self, request):
        invoices = self.get_queryset()
        wb = Workbook()
        ws = wb.active
        ws.title = "Fakturalar"

        headers = [
            'Faktura raqami', 'Partiya', 'Ombor', 'Yetkazib beruvchi',
            'Hujjat raqami', 'Hujjat sanasi', 'Miqdor', 'Narx',
            'Umumiy summa', 'Holat', 'Yaratilgan sana'
        ]
        ws.append(headers)

        for inv in invoices:
            ws.append([
                inv.invoice_number, inv.batch.batch_number,
                inv.warehouse.name, inv.supplier_name,
                inv.document_number, str(inv.document_date),
                float(inv.quantity), float(inv.price),
                float(inv.total_amount), inv.get_status_display(),
                inv.created_at.strftime('%Y-%m-%d %H:%M'),
            ])

        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        response = HttpResponse(
            buffer,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="invoices.xlsx"'
        return response

import io
from django.http import HttpResponse
from django.db.models import Sum, Count, F
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from openpyxl import Workbook
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from core.permissions import IsAdminOrKattaOrHisobchi
from apps.batches.models import Batch, BatchMovement
from apps.warehouses.models import Warehouse
from apps.batches.serializers import BatchSerializer, BatchMovementSerializer


class InventoryReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        qs = Batch.objects.select_related('product', 'warehouse', 'unit').all()

        if user.role == 'KICHIK_OMBOR_ADMINI':
            qs = qs.filter(warehouse_id=user.warehouse_id)

        warehouse_id = request.query_params.get('warehouse')
        if warehouse_id:
            qs = qs.filter(warehouse_id=warehouse_id)

        status_filter = request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)

        serializer = BatchSerializer(qs, many=True)
        total_value = qs.aggregate(total=Sum('total_value'))['total'] or 0
        total_items = qs.count()

        return Response({
            'total_items': total_items,
            'total_value': float(total_value),
            'results': serializer.data,
        })


class MovementsReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        qs = BatchMovement.objects.select_related(
            'batch', 'user', 'warehouse_from', 'warehouse_to'
        ).all()

        if user.role == 'KICHIK_OMBOR_ADMINI':
            qs = qs.filter(batch__warehouse_id=user.warehouse_id)

        movement_type = request.query_params.get('type')
        if movement_type:
            qs = qs.filter(type=movement_type)

        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)

        serializer = BatchMovementSerializer(qs[:100], many=True)
        return Response({
            'total': qs.count(),
            'results': serializer.data,
        })


class LowStockReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        qs = Batch.objects.select_related('product', 'warehouse', 'unit').filter(
            status__in=['LOW', 'EMPTY']
        )

        if user.role == 'KICHIK_OMBOR_ADMINI':
            qs = qs.filter(warehouse_id=user.warehouse_id)

        serializer = BatchSerializer(qs, many=True)
        return Response({
            'total': qs.count(),
            'results': serializer.data,
        })


class WarehouseSummaryView(APIView):
    permission_classes = [IsAdminOrKattaOrHisobchi]

    def get(self, request):
        warehouses = Warehouse.objects.filter(is_active=True)
        summary = []
        for wh in warehouses:
            batches = Batch.objects.filter(warehouse=wh)
            total_items = batches.count()
            total_value = batches.aggregate(total=Sum('total_value'))['total'] or 0
            low_stock = batches.filter(status='LOW').count()
            empty_stock = batches.filter(status='EMPTY').count()
            summary.append({
                'warehouse_id': wh.id,
                'warehouse_name': wh.name,
                'total_items': total_items,
                'total_value': float(total_value),
                'low_stock_count': low_stock,
                'empty_stock_count': empty_stock,
            })
        return Response(summary)


class ExportExcelView(APIView):
    permission_classes = [IsAdminOrKattaOrHisobchi]

    def get(self, request):
        report_type = request.query_params.get('type', 'inventory')
        wb = Workbook()
        ws = wb.active

        if report_type == 'inventory':
            ws.title = "Inventar hisoboti"
            ws.append(['Partiya raqami', 'Mahsulot', 'Ombor', 'Miqdor', 'Narx', 'Umumiy', 'Holat'])
            batches = Batch.objects.select_related('product', 'warehouse').all()
            for b in batches:
                ws.append([
                    b.batch_number, b.product.name, b.warehouse.name,
                    float(b.quantity), float(b.price), float(b.total_value),
                    b.get_status_display(),
                ])
        elif report_type == 'movements':
            ws.title = "Harakatlar hisoboti"
            ws.append(['Partiya', 'Turi', 'Miqdor', 'Oldingi', 'Keyingi', 'Foydalanuvchi', 'Sana'])
            movements = BatchMovement.objects.select_related('batch', 'user').all()[:500]
            for m in movements:
                ws.append([
                    m.batch.batch_number, m.get_type_display(),
                    float(m.quantity), float(m.balance_before),
                    float(m.balance_after),
                    str(m.user) if m.user else '-',
                    m.created_at.strftime('%Y-%m-%d %H:%M'),
                ])

        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        response = HttpResponse(
            buffer,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="report_{report_type}.xlsx"'
        return response


class ExportPDFView(APIView):
    permission_classes = [IsAdminOrKattaOrHisobchi]

    def get(self, request):
        report_type = request.query_params.get('type', 'inventory')
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
        styles = getSampleStyleSheet()
        elements = []

        if report_type == 'inventory':
            elements.append(Paragraph("Inventar hisoboti", styles['Title']))
            elements.append(Spacer(1, 0.5 * cm))

            data = [['Partiya', 'Mahsulot', 'Ombor', 'Miqdor', 'Narx', 'Jami', 'Holat']]
            batches = Batch.objects.select_related('product', 'warehouse').all()
            for b in batches:
                data.append([
                    b.batch_number, b.product.name, b.warehouse.name,
                    str(b.quantity), f"{b.price:,.2f}", f"{b.total_value:,.2f}",
                    b.get_status_display(),
                ])
        else:
            elements.append(Paragraph("Harakatlar hisoboti", styles['Title']))
            elements.append(Spacer(1, 0.5 * cm))

            data = [['Partiya', 'Turi', 'Miqdor', 'Oldingi', 'Keyingi', 'Sana']]
            movements = BatchMovement.objects.select_related('batch').all()[:200]
            for m in movements:
                data.append([
                    m.batch.batch_number, m.get_type_display(),
                    str(m.quantity), str(m.balance_before),
                    str(m.balance_after),
                    m.created_at.strftime('%Y-%m-%d'),
                ])

        if len(data) > 1:
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ]))
            elements.append(table)
        else:
            elements.append(Paragraph("Ma'lumot topilmadi", styles['Normal']))

        doc.build(elements)
        buffer.seek(0)

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="report_{report_type}.pdf"'
        return response

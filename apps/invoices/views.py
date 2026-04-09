from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from .models import ShotInvoice
from .serializers import ShotInvoiceSerializer


class ShotInvoiceViewSet(viewsets.ModelViewSet):
    serializer_class = ShotInvoiceSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filterset_fields = ['warehouse']
    search_fields = ['invoice_number']
    ordering_fields = ['created_at']
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        qs = ShotInvoice.objects.select_related(
            'batch__product', 'warehouse', 'created_by'
        ).all()
        if user.role == 'KICHIK_OMBOR_ADMINI':
            qs = qs.filter(warehouse_id=user.warehouse_id)
        return qs

    @action(detail=True, methods=['post'], url_path='upload-file')
    def upload_file(self, request, pk=None):
        """Fakturaga file yuklash."""
        invoice = self.get_object()
        file = request.FILES.get('file')
        if not file:
            return Response(
                {'error': 'File yuklang'},
                status=status.HTTP_400_BAD_REQUEST
            )
        invoice.file = file
        invoice.save()
        return Response(ShotInvoiceSerializer(invoice, context={'request': request}).data)

    @action(detail=True, methods=['delete'], url_path='remove-file')
    def remove_file(self, request, pk=None):
        """Fakturadan fileni o'chirish."""
        invoice = self.get_object()
        if invoice.file:
            invoice.file.delete(save=True)
        return Response(ShotInvoiceSerializer(invoice, context={'request': request}).data)

from decimal import Decimal
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsAdminOrKattaOmborAdmin, IsKichikOmborAdmin
from apps.batches.models import Batch
from .models import Order, OrderItem, OrderStatusHistory, Return, ReturnItem
from .serializers import (
    OrderSerializer, OrderCreateSerializer, OrderStatusUpdateSerializer,
    OrderFulfillSerializer, ReturnSerializer, ReturnCreateSerializer,
)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    filterset_fields = ['type', 'warehouse', 'status']
    search_fields = ['order_number', 'customer_name']
    ordering_fields = ['created_at', 'total_amount', 'order_date']

    def get_queryset(self):
        user = self.request.user
        qs = Order.objects.select_related('warehouse', 'created_by').prefetch_related(
            'items__product__unit', 'items__category', 'items__batch', 'status_history'
        ).all()
        if user.role == 'KICHIK_OMBOR_ADMINI':
            return qs.filter(warehouse_id=user.warehouse_id)
        return qs

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        if self.action == 'create':
            return [IsKichikOmborAdmin()]
        if self.action in ('destroy', 'update_status', 'fulfill', 'resubmit'):
            return [IsAdminOrKattaOmborAdmin()]
        if self.action in ('reject', 'accept'):
            return [IsKichikOmborAdmin()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        if self.action == 'update_status':
            return OrderStatusUpdateSerializer
        if self.action == 'fulfill':
            return OrderFulfillSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['put'], url_path='status')
    def update_status(self, request, pk=None):
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data['status']
        note = serializer.validated_data.get('note', '')

        order.status = new_status
        order.save(update_fields=['status', 'updated_at'])

        OrderStatusHistory.objects.create(
            order=order, status=new_status, note=note
        )

        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['put'], url_path='fulfill')
    def fulfill(self, request, pk=None):
        """Katta ombor admini buyurtmani bajaradi."""
        order = self.get_object()
        serializer = OrderFulfillSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        for item_data in serializer.validated_data['items']:
            try:
                order_item = OrderItem.objects.get(id=item_data['item_id'], order=order)
            except OrderItem.DoesNotExist:
                continue

            fulfilled_qty = item_data['fulfilled_quantity']
            barcode = item_data.get('barcode', '')
            batch_id = item_data.get('batch_id')

            batch = None
            if barcode:
                batch = Batch.objects.filter(barcode=barcode).first()
                if not batch:
                    batch = Batch.objects.filter(batch_number=barcode).first()
            elif batch_id:
                batch = Batch.objects.filter(id=batch_id).first()

            if batch:
                order_item.batch = batch
                order_item.price = batch.price
                order_item.barcode_scanned = barcode or batch.barcode or ''

                if fulfilled_qty > 0 and batch.quantity >= fulfilled_qty:
                    batch.update_quantity(
                        fulfilled_qty, 'OUT', request.user,
                        warehouse_from=batch.warehouse,
                        warehouse_to=order.warehouse,
                        note=f'Buyurtma {order.order_number} uchun chiqarildi',
                    )

            order_item.fulfilled_quantity = fulfilled_qty
            order_item.save()

        order.calculate_total()
        all_fulfilled = all(
            item.fulfilled_quantity >= item.quantity
            for item in order.items.all()
        )

        note = serializer.validated_data.get('note', '')
        if all_fulfilled:
            order.status = 'COMPLETED'
            order.save(update_fields=['status', 'updated_at'])
            OrderStatusHistory.objects.create(
                order=order, status='COMPLETED', note=note or "Buyurtma to'liq bajarildi"
            )
        else:
            if order.status == 'NEW':
                order.status = 'PROCESSING'
                order.save(update_fields=['status', 'updated_at'])
                OrderStatusHistory.objects.create(
                    order=order, status='PROCESSING', note=note or 'Buyurtma qisman bajarilmoqda'
                )

        return Response(OrderSerializer(order).data)

    @action(detail=False, methods=['get'], url_path='lookup-barcode')
    def lookup_barcode(self, request):
        """Barcode bo'yicha partiya qidirish."""
        barcode = request.query_params.get('barcode', '')
        if not barcode:
            return Response({'error': 'Barcode talab qilinadi'}, status=400)

        batch = Batch.objects.filter(barcode=barcode).select_related('product', 'warehouse', 'unit').first()
        if not batch:
            batch = Batch.objects.filter(batch_number=barcode).select_related('product', 'warehouse', 'unit').first()

        if not batch:
            return Response({'found': False})

        return Response({
            'found': True,
            'batch_id': batch.id,
            'batch_number': batch.batch_number,
            'barcode': batch.barcode,
            'product_id': batch.product_id,
            'product_name': batch.product.name,
            'warehouse_name': batch.warehouse.name,
            'quantity': str(batch.quantity),
            'price': str(batch.price),
            'unit': batch.unit.abbreviation if batch.unit else '',
            'status': batch.status,
        })

    @action(detail=True, methods=['put'], url_path='reject')
    def reject(self, request, pk=None):
        """Kichik ombor — hujjatda xatolik topdi, izoh bilan qaytaradi."""
        order = self.get_object()
        note = request.data.get('note', '').strip()
        if not note:
            return Response(
                {'error': 'Izoh yozish majburiy. Qanday xatolik borligini tushuntiring.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if order.status not in ('COMPLETED', 'RESUBMITTED'):
            return Response(
                {'error': 'Faqat bajarilgan yoki qayta yuborilgan buyurtmani rad etish mumkin'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = 'DOCUMENT_ERROR'
        order.save(update_fields=['status', 'updated_at'])
        OrderStatusHistory.objects.create(
            order=order, status='DOCUMENT_ERROR', note=note
        )
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['put'], url_path='accept')
    def accept(self, request, pk=None):
        """Kichik ombor — buyurtmani qabul qiladi."""
        order = self.get_object()
        if order.status not in ('COMPLETED', 'RESUBMITTED'):
            return Response(
                {'error': 'Faqat bajarilgan yoki qayta yuborilgan buyurtmani qabul qilish mumkin'},
                status=status.HTTP_400_BAD_REQUEST
            )

        note = request.data.get('note', '')
        order.status = 'ACCEPTED'
        order.save(update_fields=['status', 'updated_at'])
        OrderStatusHistory.objects.create(
            order=order, status='ACCEPTED', note=note or 'Buyurtma qabul qilindi'
        )
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['put'], url_path='resubmit')
    def resubmit(self, request, pk=None):
        """Katta ombor — tuzatib qayta yuboradi (hujjat xatoligidan keyin)."""
        order = self.get_object()
        if order.status != 'DOCUMENT_ERROR':
            return Response(
                {'error': 'Faqat hujjat xatoligi statusidagi buyurtmani qayta yuborish mumkin'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update items if provided
        items_data = request.data.get('items', [])
        for item_update in items_data:
            try:
                oi = OrderItem.objects.get(id=item_update.get('item_id'), order=order)
                if 'fulfilled_quantity' in item_update:
                    oi.fulfilled_quantity = Decimal(str(item_update['fulfilled_quantity']))
                if 'batch_id' in item_update and item_update['batch_id']:
                    batch = Batch.objects.filter(id=item_update['batch_id']).first()
                    if batch:
                        oi.batch = batch
                        oi.price = batch.price
                oi.save()
            except OrderItem.DoesNotExist:
                continue

        order.calculate_total()
        note = request.data.get('note', '')
        order.status = 'RESUBMITTED'
        order.save(update_fields=['status', 'updated_at'])
        OrderStatusHistory.objects.create(
            order=order, status='RESUBMITTED', note=note or 'Hujjat tuzatildi va qayta yuborildi'
        )
        return Response(OrderSerializer(order).data)


class ReturnViewSet(viewsets.ModelViewSet):
    """Vozvrat — kichik ombor katta omborga mahsulot qaytaradi."""
    serializer_class = ReturnSerializer
    filterset_fields = ['status', 'warehouse']
    search_fields = ['return_number']
    ordering_fields = ['created_at']

    def get_queryset(self):
        user = self.request.user
        qs = Return.objects.select_related('warehouse', 'created_by').prefetch_related(
            'items__product__unit', 'items__batch'
        ).all()
        if user.role == 'KICHIK_OMBOR_ADMINI':
            return qs.filter(warehouse_id=user.warehouse_id)
        return qs

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        if self.action == 'create':
            return [IsKichikOmborAdmin()]
        if self.action in ('accept_return', 'reject_return'):
            return [IsAdminOrKattaOmborAdmin()]
        if self.action == 'resubmit_return':
            return [IsKichikOmborAdmin()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return ReturnCreateSerializer
        return ReturnSerializer

    def create(self, request, *args, **kwargs):
        serializer = ReturnCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        ret = serializer.save()
        return Response(ReturnSerializer(ret).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['put'], url_path='accept')
    def accept_return(self, request, pk=None):
        """Katta ombor — vozvratni qabul qiladi."""
        ret = self.get_object()
        if ret.status not in ('NEW', 'RESUBMITTED'):
            return Response({'error': 'Faqat yangi vozvratni qabul qilish mumkin'}, status=400)

        from apps.warehouses.models import Warehouse
        main_wh = Warehouse.objects.filter(is_main=True).first()

        for item in ret.items.select_related('product').all():
            if main_wh:
                batch = Batch.objects.filter(product=item.product, warehouse=main_wh).first()
                if batch:
                    batch.update_quantity(
                        item.quantity, 'IN', request.user,
                        warehouse_from=ret.warehouse, warehouse_to=main_wh,
                        note=f'Vozvrat {ret.return_number}',
                    )
                    item.batch = batch
                    item.save()

        ret.status = 'ACCEPTED'
        ret.save(update_fields=['status', 'updated_at'])
        return Response(ReturnSerializer(ret).data)

    @action(detail=True, methods=['put'], url_path='reject')
    def reject_return(self, request, pk=None):
        """Katta ombor — vozvrat hujjatini rad etadi."""
        ret = self.get_object()
        note = request.data.get('note', '').strip()
        if not note:
            return Response({'error': 'Rad etish sababi majburiy'}, status=400)
        if ret.status not in ('NEW', 'RESUBMITTED'):
            return Response({'error': 'Faqat yangi vozvratni rad etish mumkin'}, status=400)
        ret.status = 'REJECTED'
        ret.reject_note = note
        ret.save(update_fields=['status', 'reject_note', 'updated_at'])
        return Response(ReturnSerializer(ret).data)

    @action(detail=True, methods=['put'], url_path='resubmit')
    def resubmit_return(self, request, pk=None):
        """Kichik ombor — tuzatib qayta yuboradi."""
        ret = self.get_object()
        if ret.status != 'REJECTED':
            return Response({'error': 'Faqat rad etilgan vozvratni qayta yuborish mumkin'}, status=400)
        items_data = request.data.get('items', [])
        for iu in items_data:
            try:
                ri = ReturnItem.objects.get(id=iu.get('item_id'), ret=ret)
                if 'quantity' in iu: ri.quantity = iu['quantity']
                if 'note' in iu: ri.note = iu['note']
                ri.save()
            except ReturnItem.DoesNotExist:
                continue
        ret.reason = request.data.get('reason', ret.reason)
        ret.status = 'RESUBMITTED'
        ret.reject_note = ''
        ret.save(update_fields=['status', 'reason', 'reject_note', 'updated_at'])
        return Response(ReturnSerializer(ret).data)

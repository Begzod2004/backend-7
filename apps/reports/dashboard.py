from django.db.models import Sum, Count
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.batches.models import Batch
from apps.warehouses.models import Warehouse
from apps.orders.models import Order
from apps.products.models import Product
from apps.users.models import CustomUser


class DashboardStatsView(APIView):
    def get(self, request):
        user = request.user

        if user.role == 'KICHIK_OMBOR_ADMINI':
            wh_id = user.warehouse_id
            batches = Batch.objects.filter(warehouse_id=wh_id)
            orders = Order.objects.filter(warehouse_id=wh_id)

            return Response({
                'warehouse_name': user.warehouse.name if user.warehouse else None,
                'total_batches': batches.count(),
                'total_products_value': float(batches.aggregate(v=Sum('total_value'))['v'] or 0),
                'low_stock_count': batches.filter(status='LOW').count(),
                'empty_stock_count': batches.filter(status='EMPTY').count(),
                'total_orders': orders.count(),
                'new_orders': orders.filter(status='NEW').count(),
                'processing_orders': orders.filter(status='PROCESSING').count(),
            })

        total_warehouses = Warehouse.objects.filter(is_active=True).count()
        total_products = Product.objects.filter(is_active=True).count()
        total_batches = Batch.objects.count()
        total_value = float(Batch.objects.aggregate(v=Sum('total_value'))['v'] or 0)
        low_stock = Batch.objects.filter(status='LOW').count()
        empty_stock = Batch.objects.filter(status='EMPTY').count()
        total_orders = Order.objects.count()
        new_orders = Order.objects.filter(status='NEW').count()
        total_users = CustomUser.objects.filter(is_active=True).count()

        stats = {
            'total_warehouses': total_warehouses,
            'total_products': total_products,
            'total_batches': total_batches,
            'total_products_value': total_value,
            'low_stock_count': low_stock,
            'empty_stock_count': empty_stock,
            'total_orders': total_orders,
            'new_orders': new_orders,
            'total_users': total_users,
        }

        if user.role == 'HISOBCHI':
            from apps.invoices.models import ShotInvoice
            stats['total_invoices'] = ShotInvoice.objects.count()
            stats['pending_invoices'] = ShotInvoice.objects.filter(file='').count()

        return Response(stats)

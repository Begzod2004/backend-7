from django.db.models import Sum, Count
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.batches.models import Batch
from apps.warehouses.models import Warehouse
from apps.objects.models import ConstructionObject, ObjectExpense
from apps.batches.serializers import BatchSerializer
from datetime import timedelta


class DashboardChartsView(APIView):
    def get(self, request):
        now = timezone.now()

        # Monthly expenses (last 6 months from ObjectExpense)
        monthly_expenses = []
        for i in range(5, -1, -1):
            month_start = (now - timedelta(days=30 * i)).replace(day=1)
            if i > 0:
                month_end = (now - timedelta(days=30 * (i - 1))).replace(day=1)
            else:
                month_end = now
            total = ObjectExpense.objects.filter(
                created_at__gte=month_start, created_at__lt=month_end
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            monthly_expenses.append({
                'month': month_start.strftime('%Y-%m'),
                'amount': float(total),
            })

        # Top 5 materials by expense quantity
        from django.db.models import F
        top_materials = list(
            ObjectExpense.objects.values(
                product_name=F('batch__product__name'),
                unit=F('batch__unit__abbreviation'),
            ).annotate(
                total_used=Sum('quantity')
            ).order_by('-total_used')[:5]
        )
        for m in top_materials:
            m['total_used'] = float(m['total_used'])

        # Warehouse fill percentage
        warehouse_fill = []
        for wh in Warehouse.objects.filter(is_active=True):
            batches = Batch.objects.filter(warehouse=wh)
            total_value = float(batches.aggregate(v=Sum('total_value'))['v'] or 0)
            batch_count = batches.count()
            fill_pct = min(100, int((batch_count / max(wh.capacity, 1)) * 100)) if wh.capacity > 0 else 0
            warehouse_fill.append({
                'warehouse': wh.name,
                'fill_percent': fill_pct,
                'total_value': total_value,
            })

        # Active objects budget vs spent
        object_budget = []
        for obj in ConstructionObject.objects.filter(status='ACTIVE'):
            spent = float(obj.expenses.aggregate(s=Sum('total_amount'))['s'] or 0)
            object_budget.append({
                'object_name': obj.name,
                'budget': float(obj.budget),
                'spent': spent,
            })

        # Stock alerts
        low_batches = Batch.objects.filter(status__in=['LOW', 'EMPTY']).select_related('product', 'warehouse', 'unit')
        stock_alerts = {
            'low_count': low_batches.filter(status='LOW').count(),
            'empty_count': low_batches.filter(status='EMPTY').count(),
            'items': BatchSerializer(low_batches[:10], many=True).data,
        }

        return Response({
            'monthly_expenses': monthly_expenses,
            'top_materials': top_materials,
            'warehouse_fill': warehouse_fill,
            'object_budget': object_budget,
            'stock_alerts': stock_alerts,
        })

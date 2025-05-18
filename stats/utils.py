from django.db.models import Sum, F, ExpressionWrapper, DecimalField, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from inventory.models import Product, Category, StockMovement
from orders.models import Order, OrderItem
from invoices.models import Invoice, Payment

def get_dashboard_stats():
    """استخراج البيانات الأساسية للوحة التحكم الرئيسية"""
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    
    # إحصائيات المنتجات
    products = Product.objects.all()
    total_products = products.count()
    low_stock_count = products.filter(quantity__lte=F('reorder_level')).count()
    
    # حساب قيمة المخزون
    stock_value = products.aggregate(
        value=Sum(ExpressionWrapper(F('quantity') * F('cost_price'), output_field=DecimalField()))
    )['value'] or 0
    
    # طلبات اليوم
    today_orders = Order.objects.filter(created_at__date=today).count()
    
    # طلبات الشهر
    orders_this_month = Order.objects.filter(created_at__date__gte=start_of_month).count()
    
    # مبيعات اليوم
    today_sales = OrderItem.objects.filter(
        order__created_at__date=today,
        order__status='COMPLETED'
    ).aggregate(
        sales=Sum(ExpressionWrapper(F('quantity') * F('price'), output_field=DecimalField()))
    )['sales'] or 0
    
    # مبيعات الشهر
    monthly_sales = OrderItem.objects.filter(
        order__created_at__date__gte=start_of_month,
        order__status='COMPLETED'
    ).aggregate(
        sales=Sum(ExpressionWrapper(F('quantity') * F('price'), output_field=DecimalField()))
    )['sales'] or 0
    
    return {
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'stock_value': stock_value,
        'today_orders': today_orders,
        'orders_this_month': orders_this_month,
        'today_sales': today_sales,
        'monthly_sales': monthly_sales
    }

def get_monthly_sales_data(year=None):
    """استخراج بيانات المبيعات الشهرية للسنة المحددة"""
    if not year:
        year = timezone.now().year
    
    # قائمة بأسماء الأشهر باللغة الإنجليزية
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    
    # قائمة لتخزين بيانات المبيعات
    sales_data = [0] * 12
    
    # استعلام عن مبيعات كل شهر
    for month in range(1, 13):
        try:
            month_sales = OrderItem.objects.filter(
                order__created_at__year=year,
                order__created_at__month=month,
                order__status='COMPLETED'
            ).aggregate(
                sales=Sum(ExpressionWrapper(F('quantity') * F('price'), output_field=DecimalField()))
            )['sales'] or 0
        except:
            month_sales = 0
        
        sales_data[month - 1] = float(month_sales)
    
    return {
        'labels': months,
        'data': sales_data
    }

def get_top_selling_products(limit=5, period=30):
    """استخراج قائمة المنتجات الأكثر مبيعًا"""
    start_date = timezone.now().date() - timedelta(days=period)
    
    top_products = OrderItem.objects.filter(
        order__created_at__date__gte=start_date,
        order__status='COMPLETED'
    ).values(
        'product__id', 'product__name', 'product__sku'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_sales=Sum(ExpressionWrapper(F('quantity') * F('price'), output_field=DecimalField()))
    ).order_by('-total_quantity')[:limit]
    
    return list(top_products)

def get_low_stock_stats():
    """استخراج إحصائيات المنتجات ذات المخزون المنخفض"""
    low_stock_products = Product.objects.filter(
        quantity__lte=F('reorder_level'),
        is_active=True
    ).order_by('quantity')
    
    critical_stock = low_stock_products.filter(quantity=0).count()
    warning_stock = low_stock_products.exclude(quantity=0).count()
    
    return {
        'low_stock_products': low_stock_products[:10],  # أول 10 منتجات فقط
        'total_low_stock': low_stock_products.count(),
        'critical_stock': critical_stock,
        'warning_stock': warning_stock
    }

def get_payment_stats():
    """استخراج إحصائيات المدفوعات"""
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    
    # إجمالي الفواتير
    total_invoices = Invoice.objects.count()
    
    # الفواتير المستحقة
    pending_invoices = Invoice.objects.filter(status='PENDING').count()
    
    # الفواتير المدفوعة
    paid_invoices = Invoice.objects.filter(status='PAID').count()
    
    # إجمالي المدفوعات هذا الشهر
    month_payments = Invoice.objects.filter(
        payments__payment_date__gte=start_of_month
    ).aggregate(
        total=Sum('payments__amount')
    )['total'] or 0
    
    return {
        'total_invoices': total_invoices,
        'pending_invoices': pending_invoices,
        'paid_invoices': paid_invoices,
        'payment_rate': (paid_invoices / total_invoices * 100) if total_invoices > 0 else 0,
        'month_payments': month_payments
    }
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F, Q, ExpressionWrapper, DecimalField
from django.utils import timezone
from datetime import datetime, timedelta
from inventory.models import Product, Category, StockMovement
from orders.models import Order, OrderItem
from invoices.models import Invoice, Payment
from .utils import get_top_selling_products, get_low_stock_stats, get_payment_stats, get_monthly_sales_data
from users.decorators import admin_required, employee_required

@login_required
@employee_required
def statistics_view(request):
    period = request.GET.get('period', '30')  # افتراضي: 30 يوم
    try:
        period = int(period)
    except ValueError:
        period = 30
    
    today = timezone.now().date()
    start_date = today - timedelta(days=period)
    
    # البيانات الأساسية
    context = {
        'title': 'Statistics',
        'period': period,
        'start_date': start_date,
        'today': today
    }
    
    # إحصائيات المبيعات
    sales_stats = get_sales_stats(start_date)
    context.update(sales_stats)
    
    # إحصائيات المنتجات
    product_stats = get_product_stats()
    context.update(product_stats)
    
    # إحصائيات المدفوعات
    payment_stats = get_payment_stats()
    context.update(payment_stats)
    
    # المنتجات الأكثر مبيعًا
    context['top_selling_products'] = get_top_selling_products(limit=10, period=period)
    
    # بيانات المبيعات الشهرية للرسم البياني
    context['monthly_sales_data'] = get_monthly_sales_data()
    
    # إحصائيات المخزون المنخفض
    context.update(get_low_stock_stats())
    
    # توزيع الطلبات حسب الحالة
    order_status_distribution = Order.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # تحويل البيانات للرسم البياني
    status_labels = []
    status_data = []
    status_colors = {
        'PENDING': '#f6c23e',       # أصفر
        'IN_PROGRESS': '#4e73df',   # أزرق
        'COMPLETED': '#1cc88a',     # أخضر
        'CANCELLED': '#e74a3b',     # أحمر
        'REJECTED': '#858796'       # رمادي
    }
    status_colors_list = []
    
    for item in order_status_distribution:
        status_display = dict(Order.OrderStatus.choices)[item['status']]
        status_labels.append(status_display)
        status_data.append(item['count'])
        status_colors_list.append(status_colors.get(item['status'], '#858796'))
    
    context['order_status_labels'] = status_labels
    context['order_status_data'] = status_data
    context['order_status_colors'] = status_colors_list
    
    # توزيع المنتجات حسب الفئات
    category_distribution = Category.objects.annotate(
        products_count=Count('products')
    ).values('name', 'products_count').order_by('-products_count')
    
    # تحويل البيانات للرسم البياني
    category_labels = []
    category_data = []
    
    for item in category_distribution:
        category_labels.append(item['name'])
        category_data.append(item['products_count'])
    
    context['category_labels'] = category_labels
    context['category_data'] = category_data
    
    return render(request, 'stats/statistics.html', context)

def get_sales_stats(start_date):
    """إحصائيات المبيعات"""
    # إجمالي الطلبات
    total_orders = Order.objects.count()
    
    # طلبات الفترة
    period_orders = Order.objects.filter(created_at__date__gte=start_date).count()
    
    # الطلبات المكتملة
    completed_orders = Order.objects.filter(status=Order.OrderStatus.COMPLETED).count()
    
    # نسبة إكمال الطلبات
    completion_rate = (completed_orders / total_orders * 100) if total_orders > 0 else 0
    
    # إجمالي المبيعات
    total_sales = OrderItem.objects.filter(
        order__status=Order.OrderStatus.COMPLETED
    ).aggregate(
        sales=Sum(ExpressionWrapper(F('quantity') * F('price'), output_field=DecimalField()))
    )['sales'] or 0
    
    # مبيعات الفترة
    period_sales = OrderItem.objects.filter(
        order__status=Order.OrderStatus.COMPLETED,
        order__created_at__date__gte=start_date
    ).aggregate(
        sales=Sum(ExpressionWrapper(F('quantity') * F('price'), output_field=DecimalField()))
    )['sales'] or 0
    
    # متوسط قيمة الطلب
    avg_order_value = total_sales / completed_orders if completed_orders > 0 else 0
    
    return {
        'total_orders': total_orders,
        'period_orders': period_orders,
        'completed_orders': completed_orders,
        'completion_rate': completion_rate,
        'total_sales': total_sales,
        'period_sales': period_sales,
        'avg_order_value': avg_order_value
    }

def get_product_stats():
    """إحصائيات المنتجات"""
    # إجمالي المنتجات
    total_products = Product.objects.count()
    
    # المنتجات النشطة
    active_products = Product.objects.filter(is_active=True).count()
    
    # عدد الفئات
    categories_count = Category.objects.count()
    
    # إجمالي قيمة المخزون
    stock_value = Product.objects.aggregate(
        value=Sum(ExpressionWrapper(F('quantity') * F('cost_price'), output_field=DecimalField()))
    )['value'] or 0
    
    stock_movements_count = StockMovement.objects.count()
    
    return {
        'total_products': total_products,
        'active_products': active_products,
        'categories_count': categories_count,
        'stock_value': stock_value,
        'stock_movements_count': stock_movements_count
    }
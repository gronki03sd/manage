from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from stats.utils import get_dashboard_stats, get_monthly_sales_data

@login_required
def dashboard_view(request):
    """Dashboard view - requires login"""
    # Différencier l'affichage selon le rôle de l'utilisateur
    if request.user.role == 'CLIENT':
        return client_dashboard(request)
    else:
        return staff_dashboard(request)

def staff_dashboard(request):
    """Dashboard for staff and admin"""
    stats_data = get_dashboard_stats()
    
    # Calcul du nombre de produits à stock normal
    normal_stock_count = stats_data['total_products'] - stats_data['low_stock_count']
    
    # Récupération des données de ventes mensuelles
    monthly_sales = get_monthly_sales_data()
    
    # Modification des noms de mois en anglais
    english_months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    monthly_sales['labels'] = english_months
    
    context = {
        'title': 'Dashboard',
        'stats': stats_data,
        'sales_data': monthly_sales,
        'normal_stock_count': normal_stock_count,
        'user_role': request.user.role
    }
    return render(request, 'dashboard/index.html', context)

def client_dashboard(request):
    """Dashboard pour les clients - montrer uniquement leurs commandes et factures"""
    # Récupérez les commandes du client
    orders = request.user.orders.all().order_by('-created_at')[:5]
    
    # Si le client a des factures liées à ses commandes
    invoices = []
    for order in orders:
        if hasattr(order, 'invoice'):
            invoices.append(order.invoice)
    
    context = {
        'title': 'Client Dashboard',
        'orders': orders,
        'invoices': invoices,
        'user_role': request.user.role
    }
    return render(request, 'dashboard/client_dashboard.html', context)
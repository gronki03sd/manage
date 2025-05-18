from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, F, ExpressionWrapper, DecimalField
from django.core.paginator import Paginator
from .models import Order, OrderItem
from inventory.models import Product
from users.models import User
from django import forms
from django.http import JsonResponse
import json
from users.decorators import admin_required, employee_required

@login_required
@employee_required
def orders_list(request):
    orders = Order.objects.all().order_by('-created_at')
    
    context = {
        'page_obj': orders,
        'title': 'Liste des Commandes'
    }
    
    return render(request, 'orders/orders_list.html', context)

@login_required
@employee_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    items = order.items.all()
    
    context = {
        'order': order,
        'items': items,
        'title': f'Commande #{order.order_number}'
    }
    
    return render(request, 'orders/order_detail.html', context)

@login_required
@employee_required
def order_create(request):
    clients = User.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            client_id = data.get('client')
            notes = data.get('notes', '')
            items = data.get('items', [])
            
            if not client_id or not items:
                return JsonResponse({'status': 'error', 'message': 'Le client et les articles sont requis'}, status=400)
            
            client = User.objects.get(id=client_id)
            order = Order.objects.create(
                client=client,
                notes=notes,
                created_by=request.user
            )
            
            # Ajouter les articles de la commande
            for item in items:
                product = Product.objects.get(id=item['product_id'])
                quantity = int(item['quantity'])
                price = float(item['price']) if 'price' in item else product.selling_price
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=price
                )
            
            return JsonResponse({
                'status': 'success',
                'message': f'Commande #{order.order_number} créée avec succès',
                'order_id': order.id
            })
        
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    context = {
        'clients': clients,
        'products': products,
        'title': 'Créer une Commande'
    }
    
    return render(request, 'orders/order_form.html', context)

@login_required
@employee_required
def order_status_update(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        if status and status in dict(Order.OrderStatus.choices).keys():
            order.status = status
            order.save()
            messages.success(request, f'Statut de la commande modifié à {order.get_status_display()}')
        else:
            messages.error(request, 'Statut invalide')
        
        return redirect('order-detail', pk=order.pk)
    
    statuses = Order.OrderStatus.choices
    
    context = {
        'order': order,
        'statuses': statuses,
        'title': f'Mettre à jour le statut de la commande: #{order.order_number}'
    }
    
    return render(request, 'orders/order_status_form.html', context)
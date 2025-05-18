# inventory/views.py (code complet)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, F, ExpressionWrapper, DecimalField
from django.core.paginator import Paginator
from .models import Product, Category, StockMovement
from .forms import ProductForm, CategoryForm, StockMovementForm
from users.decorators import admin_required, employee_required

# Views for Products
@login_required
@employee_required
def product_list(request):
    search_query = request.GET.get('search', '')
    category_id = request.GET.get('category', '')
    
    products = Product.objects.all()
    
    # Appliquer la recherche
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(sku__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filtrer par catégorie
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Trier les produits
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'quantity':
        products = products.order_by('quantity')
    elif sort_by == '-quantity':
        products = products.order_by('-quantity')
    elif sort_by == 'price':
        products = products.order_by('selling_price')
    elif sort_by == '-price':
        products = products.order_by('-selling_price')
    else:
        products = products.order_by('name')
    
    # Statistiques d'inventaire
    total_products = products.count()
    total_value = products.aggregate(
        total=Sum(ExpressionWrapper(F('quantity') * F('cost_price'), output_field=DecimalField()))
    )['total'] or 0
    low_stock_count = products.filter(quantity__lte=F('reorder_level')).count()
    
    # Pagination
    paginator = Paginator(products, 10)  # 10 produits par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Liste des catégories pour le filtre
    categories = Category.objects.all()
    
    context = {
        'page_obj': page_obj,
        'total_products': total_products,
        'total_value': total_value,
        'low_stock_count': low_stock_count,
        'search_query': search_query,
        'categories': categories,
        'selected_category': category_id,
        'sort_by': sort_by,
        'title': 'Liste des Produits'
    }
    
    return render(request, 'inventory/product_list.html', context)

@login_required
@employee_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    # Derniers mouvements de stock pour ce produit
    stock_movements = StockMovement.objects.filter(product=product).order_by('-created_at')[:10]
    
    context = {
        'product': product,
        'stock_movements': stock_movements,
        'title': product.name
    }
    
    return render(request, 'inventory/product_detail.html', context)

@login_required
@employee_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            
            # Créer un mouvement de stock initial si la quantité est > 0
            initial_quantity = form.cleaned_data['quantity']
            if initial_quantity > 0:
                StockMovement.objects.create(
                    product=product,
                    movement_type=StockMovement.MOVEMENT_IN,
                    quantity=initial_quantity,
                    reference='Stock Initial',
                    created_by=request.user
                )
            
            messages.success(request, f'Le produit "{product.name}" a été créé avec succès.')
            return redirect('product-list')
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'title': 'Ajouter un Produit'
    }
    
    return render(request, 'inventory/product_form.html', context)

@login_required
@employee_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    original_quantity = product.quantity
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            new_quantity = form.cleaned_data['quantity']
            product = form.save()
            
            # Créer un mouvement de stock si la quantité a changé
            if new_quantity != original_quantity:
                if new_quantity > original_quantity:
                    # Ajout de stock
                    movement_type = StockMovement.MOVEMENT_IN
                    quantity = new_quantity - original_quantity
                else:
                    # Réduction de stock
                    movement_type = StockMovement.MOVEMENT_OUT
                    quantity = original_quantity - new_quantity
                
                StockMovement.objects.create(
                    product=product,
                    movement_type=movement_type,
                    quantity=quantity,
                    reference='Ajustement Manuel',
                    created_by=request.user
                )
            
            messages.success(request, f'Le produit "{product.name}" a été mis à jour avec succès.')
            return redirect('product-detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'product': product,
        'title': f'Modifier le Produit: {product.name}'
    }
    
    return render(request, 'inventory/product_form.html', context)

@login_required
@admin_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Le produit "{product_name}" a été supprimé avec succès.')
        return redirect('product-list')
    
    context = {
        'product': product,
        'title': f'Supprimer le Produit: {product.name}'
    }
    
    return render(request, 'inventory/product_confirm_delete.html', context)

# Views for Categories
@login_required
@admin_required
def category_list(request):
    categories = Category.objects.all().order_by('name')
    
    # Statistiques pour chaque catégorie
    for category in categories:
        category.product_count = Product.objects.filter(category=category).count()
    
    context = {
        'categories': categories,
        'title': 'Catégories'
    }
    
    return render(request, 'inventory/category_list.html', context)

@login_required
@admin_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'La catégorie "{category.name}" a été créée avec succès.')
            return redirect('category-list')
    else:
        form = CategoryForm()
    
    context = {
        'form': form,
        'title': 'Ajouter une Catégorie'
    }
    
    return render(request, 'inventory/category_form.html', context)

@login_required
@admin_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'La catégorie "{category.name}" a été mise à jour avec succès.')
            return redirect('category-list')
    else:
        form = CategoryForm(instance=category)
    
    context = {
        'form': form,
        'category': category,
        'title': f'Modifier la Catégorie: {category.name}'
    }
    
    return render(request, 'inventory/category_form.html', context)

@login_required
@admin_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(request, f'La catégorie "{category_name}" a été supprimée avec succès.')
        return redirect('category-list')
    
    context = {
        'category': category,
        'title': f'Supprimer la Catégorie: {category.name}'
    }
    
    return render(request, 'inventory/category_confirm_delete.html', context)

# Views for Stock Movements
@login_required
@employee_required
def stock_movement_list(request):
    product_id = request.GET.get('product', '')
    movement_type = request.GET.get('type', '')
    
    stock_movements = StockMovement.objects.all()
    
    if product_id:
        stock_movements = stock_movements.filter(product_id=product_id)
    
    if movement_type:
        stock_movements = stock_movements.filter(movement_type=movement_type)
    
    stock_movements = stock_movements.order_by('-created_at')
    
    paginator = Paginator(stock_movements, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    products = Product.objects.all().order_by('name')
    
    context = {
        'page_obj': page_obj,
        'products': products,
        'selected_product': product_id,
        'selected_type': movement_type,
        'movement_types': StockMovement.MOVEMENT_TYPES,
        'title': 'Mouvements de Stock'
    }
    
    return render(request, 'inventory/stock_movement_list.html', context)

@login_required
@employee_required
def stock_movement_create(request):
    initial_product = request.GET.get('product', None)
    initial_data = {}
    
    if initial_product:
        initial_data['product'] = initial_product
    
    if request.method == 'POST':
        form = StockMovementForm(request.POST, initial=initial_data)
        if form.is_valid():
            stock_movement = form.save(commit=False)
            stock_movement.created_by = request.user
            
            try:
                stock_movement.save()
                messages.success(request, f'Le mouvement de stock a été enregistré avec succès.')
                
                # Retour à la page du produit si spécifié
                if 'product' in request.GET:
                    return redirect('product-detail', pk=request.GET['product'])
                return redirect('stock-movement-list')
            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = StockMovementForm(initial=initial_data)
    
    context = {
        'form': form,
        'title': 'Ajouter un Mouvement de Stock'
    }
    
    return render(request, 'inventory/stock_movement_form.html', context)

@login_required
@employee_required
def low_stock_products(request):
    products = Product.objects.filter(
        quantity__lte=F('reorder_level'),
        is_active=True
    ).order_by('quantity')
    
    context = {
        'products': products,
        'title': 'Produits à Stock Faible'
    }
    
    return render(request, 'inventory/low_stock_products.html', context)
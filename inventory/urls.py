from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='inventory-list'),
    path('products/', views.product_list, name='product-list'),
    path('products/<int:pk>/', views.product_detail, name='product-detail'),
    path('products/create/', views.product_create, name='product-create'),
    path('products/<int:pk>/update/', views.product_update, name='product-update'),
    path('products/<int:pk>/delete/', views.product_delete, name='product-delete'),
    
    path('categories/', views.category_list, name='category-list'),
    path('categories/create/', views.category_create, name='category-create'),
    path('categories/<int:pk>/update/', views.category_update, name='category-update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category-delete'),
    
    path('stock-movements/', views.stock_movement_list, name='stock-movement-list'),
    path('stock-movements/create/', views.stock_movement_create, name='stock-movement-create'),
    
    path('low-stock/', views.low_stock_products, name='low-stock-products'),
]
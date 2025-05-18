from django.urls import path
from . import views

urlpatterns = [
    path('', views.orders_list, name='orders-list'),
    path('create/', views.order_create, name='order-create'),
    path('<int:pk>/', views.order_detail, name='order-detail'),
    path('<int:pk>/status/', views.order_status_update, name='order-status-update'),
]
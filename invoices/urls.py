from django.urls import path
from . import views

urlpatterns = [
    path('', views.invoices_list, name='invoices-list'),
    path('<int:pk>/', views.invoice_detail, name='invoice-detail'),
    path('create/<int:order_id>/', views.invoice_create, name='invoice-create'),
    path('<int:pk>/payment/add/', views.add_payment, name='add-payment'),
    path('<int:pk>/pdf/', views.generate_pdf, name='invoice-pdf'),
]
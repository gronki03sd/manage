from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Sum, Q
from django.core.paginator import Paginator
from .models import Invoice, Payment
from orders.models import Order
from django import forms
from django.http import JsonResponse
import json
import io
from django.template.loader import get_template
from xhtml2pdf import pisa
from users.decorators import admin_required, employee_required

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'method', 'reference', 'notes', 'payment_date']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.invoice = kwargs.pop('invoice', None)
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        
        if self.invoice:
            # Fix for TypeError: handle None values correctly
            total_paid = self.invoice.payments.aggregate(total=Sum('amount'))['total']
            if total_paid is None:
                total_paid = 0
                
            # Ensure invoice.total_amount is not None
            if self.invoice.total_amount is not None:
                remaining = self.invoice.total_amount - total_paid
            else:
                remaining = 0
                
            self.fields['amount'].initial = remaining

@login_required
@employee_required
def invoices_list(request):
    invoices = Invoice.objects.all().order_by('-issue_date')
    
    context = {
        'page_obj': invoices,
        'invoice_statuses': Invoice.InvoiceStatus.choices,
        'title': 'Liste des Factures'
    }
    
    return render(request, 'invoices/invoices_list.html', context)

@login_required
@employee_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    payments = invoice.payments.all().order_by('-payment_date')
    
    # Safely handle None values
    total_paid = payments.aggregate(total=Sum('amount'))['total']
    if total_paid is None:
        total_paid = 0
        
    # Ensure invoice.total_amount is not None
    if invoice.total_amount is not None:
        remaining = invoice.total_amount - total_paid
    else:
        remaining = 0
    
    context = {
        'invoice': invoice,
        'payments': payments,
        'order_items': invoice.order.items.all(),
        'total_paid': total_paid,
        'remaining': remaining,
        'title': f'Facture #{invoice.invoice_number}'
    }
    
    return render(request, 'invoices/invoice_detail.html', context)

@login_required
@employee_required
def invoice_create(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    
    # Check if invoice already exists
    if hasattr(order, 'invoice'):
        messages.error(request, f'Une facture existe déjà pour la commande #{order.order_number}')
        return redirect('order-detail', pk=order.pk)
    
    if request.method == 'POST':
        tax_rate = float(request.POST.get('tax_rate', 0))
        discount = float(request.POST.get('discount', 0))
        notes = request.POST.get('notes', '')
        
        invoice = Invoice.objects.create(
            order=order,
            tax_rate=tax_rate,
            discount=discount,
            notes=notes,
            created_by=request.user
        )
        
        messages.success(request, f'Facture #{invoice.invoice_number} créée avec succès.')
        return redirect('invoice-detail', pk=invoice.pk)
    
    context = {
        'order': order,
        'title': f'Créer une facture pour la commande #{order.order_number}'
    }
    
    return render(request, 'invoices/invoice_form.html', context)

@login_required
@employee_required
def add_payment(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    
    # Calculate remaining amount - safely handling None values
    total_paid = invoice.payments.aggregate(total=Sum('amount'))['total']
    if total_paid is None:
        total_paid = 0
        
    # Ensure invoice.total_amount is not None
    if invoice.total_amount is not None:
        remaining = invoice.total_amount - total_paid
    else:
        remaining = 0
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, invoice=invoice)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.invoice = invoice
            payment.created_by = request.user
            
            # Check if payment amount exceeds remaining
            if payment.amount > remaining:
                messages.error(request, f'Le montant du paiement dépasse le solde restant (${remaining}).')
                return redirect('add-payment', pk=invoice.pk)
            
            payment.save()
            
            messages.success(request, f'Paiement de ${payment.amount} enregistré avec succès.')
            return redirect('invoice-detail', pk=invoice.pk)
    else:
        form = PaymentForm(invoice=invoice)
    
    context = {
        'form': form,
        'invoice': invoice,
        'remaining': remaining,
        'title': f'Ajouter un paiement à la facture #{invoice.invoice_number}'
    }
    
    return render(request, 'invoices/payment_form.html', context)

@login_required
@employee_required
def generate_pdf(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    
    # Get data for PDF - safely handle None values
    payments = invoice.payments.all()
    total_paid = payments.aggregate(total=Sum('amount'))['total']
    if total_paid is None:
        total_paid = 0
    
    context = {
        'invoice': invoice,
        'order_items': invoice.order.items.all(),
        'payments': payments,
        'total_paid': total_paid,
    }
    
    # Render HTML template
    template = get_template('invoices/invoice_pdf.html')
    html = template.render(context)
    
    # Create PDF
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{invoice.invoice_number}.pdf"'
        return response
    
    return HttpResponse('Erreur lors de la génération du PDF', status=400)
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SettingsForm
from .models import Setting
from users.decorators import admin_required

def get_setting(key, default=''):
    try:
        setting = Setting.objects.get(key=key)
        return setting.value
    except Setting.DoesNotExist:
        return default

def set_setting(key, value):
    setting, created = Setting.objects.get_or_create(key=key)
    setting.value = value
    setting.save()
    return setting

@login_required
@admin_required
def settings_view(request):
    # Load existing settings
    initial_data = {
        'company_name': get_setting('company_name', 'My Company'),
        'company_email': get_setting('company_email', 'info@mycompany.com'),
        'company_phone': get_setting('company_phone', '+1234567890'),
        'company_website': get_setting('company_website', 'https://www.mycompany.com'),
        'company_address': get_setting('company_address', '123 Main St, City, Country'),
        'default_tax_rate': get_setting('default_tax_rate', '15.0'),
        'default_currency': get_setting('default_currency', 'USD'),
    }
    
    if request.method == 'POST':
        form = SettingsForm(request.POST)
        if form.is_valid():
            # Save settings
            for key, value in form.cleaned_data.items():
                set_setting(key, str(value) if value is not None else '')
            
            messages.success(request, 'Settings have been updated successfully.')
            return redirect('settings')
    else:
        form = SettingsForm(initial=initial_data)
    
    context = {
        'form': form,
        'title': 'Settings'
    }
    
    return render(request, 'settings_app/settings.html', context)
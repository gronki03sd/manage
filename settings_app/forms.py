from django import forms

class SettingsForm(forms.Form):
    company_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    company_email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    company_phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    company_website = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))
    company_address = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    
    default_tax_rate = forms.DecimalField(max_digits=5, decimal_places=2, required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    default_currency = forms.CharField(max_length=3, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
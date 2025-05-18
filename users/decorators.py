from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def admin_required(function):
    """Décorateur pour restreindre l'accès aux administrateurs uniquement"""
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'ADMIN':
            return function(request, *args, **kwargs)
        else:
            messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette page.")
            return redirect('dashboard')
    return wrap

def employee_required(function):
    """Décorateur pour restreindre l'accès aux employés et administrateurs"""
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.role == 'EMPLOYEE' or request.user.role == 'ADMIN'):
            return function(request, *args, **kwargs)
        else:
            messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette page.")
            return redirect('dashboard')
    return wrap

def client_required(function):
    """Décorateur pour restreindre l'accès aux clients"""
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'CLIENT':
            return function(request, *args, **kwargs)
        else:
            messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette page.")
            return redirect('dashboard')
    return wrap
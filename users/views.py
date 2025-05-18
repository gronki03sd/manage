from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views import View
from django.contrib import messages

from .models import User
from .forms import LoginForm, UserRegistrationForm, UserUpdateForm, ProfileUpdateForm, EmployeeRegistrationForm
from .decorators import admin_required, employee_required

# Authentication Views
class CustomLoginView(View):
    template_name = 'users/login.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = LoginForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
        
        return render(request, self.template_name, {'form': form})

class CustomLogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, 'Vous avez été déconnecté avec succès.')
        return redirect('login')

class UserRegisterView(View):
    form_class = UserRegistrationForm
    template_name = 'users/register.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Compte créé pour {username}. Vous pouvez maintenant vous connecter.')
            return redirect('login')
        return render(request, self.template_name, {'form': form})

# User Profile
@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    context = {
        'form': form,
        'title': 'Profil'
    }
    return render(request, 'users/profile.html', context)

# User Management (Admin Only)
@login_required
@admin_required
def users_list(request):
    users = User.objects.all()
    
    # Compter les utilisateurs par rôle
    admin_count = users.filter(role='ADMIN').count()
    employee_count = users.filter(role='EMPLOYEE').count()
    client_count = users.filter(role='CLIENT').count()
    
    context = {
        'users': users,
        'admin_count': admin_count,
        'employee_count': employee_count,
        'client_count': client_count,
        'title': 'Liste des Utilisateurs'
    }
    return render(request, 'users/users_list.html', context)

@login_required
@admin_required
def user_create(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'L\'utilisateur {username} a été créé avec succès.')
            return redirect('users-list')
    else:
        form = UserRegistrationForm()
    
    context = {
        'form': form,
        'title': 'Créer un Utilisateur'
    }
    return render(request, 'users/user_form.html', context)

@login_required
@admin_required
def employee_create(request):
    """Vue pour créer un compte employé (réservée aux administrateurs)"""
    if request.method == 'POST':
        form = EmployeeRegistrationForm(request.POST)
        if form.is_valid():
            # Créer l'utilisateur mais ne pas encore sauvegarder
            user = form.save(commit=False)
            # Définir le rôle comme EMPLOYEE
            user.role = 'EMPLOYEE'
            # Sauvegarder maintenant
            user.save()
            
            username = form.cleaned_data.get('username')
            messages.success(request, f'Le compte employé "{username}" a été créé avec succès.')
            return redirect('users-list')
    else:
        form = EmployeeRegistrationForm()
    
    context = {
        'form': form,
        'title': 'Créer un Compte Employé',
        'employee_form': True
    }
    
    return render(request, 'users/employee_form.html', context)

@login_required
@admin_required
def user_update(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'L\'utilisateur {user_obj.username} a été mis à jour avec succès.')
            return redirect('users-list')
    else:
        form = UserUpdateForm(instance=user_obj)
    
    context = {
        'form': form,
        'title': f'Modifier l\'utilisateur: {user_obj.username}'
    }
    return render(request, 'users/user_form.html', context)

@login_required
@admin_required
def user_delete(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        username = user_obj.username
        user_obj.delete()
        messages.success(request, f'L\'utilisateur {username} a été supprimé avec succès.')
        return redirect('users-list')
    
    context = {
        'user_obj': user_obj,
        'title': f'Supprimer l\'utilisateur: {user_obj.username}'
    }
    return render(request, 'users/user_confirm_delete.html', context)
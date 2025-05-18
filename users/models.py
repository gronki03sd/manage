from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """Modèle utilisateur personnalisé avec différents rôles"""
    
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Admin')
        EMPLOYEE = 'EMPLOYEE', _('Employee')
        CLIENT = 'CLIENT', _('Client')
    
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.EMPLOYEE,
        verbose_name=_('Role')
    )
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name=_('Phone Number'))
    profile_pic = models.ImageField(upload_to='profile_pics', default='default.png', verbose_name=_('Profile Picture'))
    address = models.TextField(blank=True, null=True, verbose_name=_('Address'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN
        
    @property
    def is_employee(self):
        return self.role == self.Role.EMPLOYEE
        
    @property
    def is_client(self):
        return self.role == self.Role.CLIENT

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
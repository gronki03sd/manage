from django.db import models
from django.utils.translation import gettext_lazy as _

class Setting(models.Model):
    key = models.CharField(max_length=50, unique=True, verbose_name=_('Key'))
    value = models.TextField(verbose_name=_('Value'))
    
    def __str__(self):
        return self.key
    
    class Meta:
        verbose_name = _('Setting')
        verbose_name_plural = _('Settings')
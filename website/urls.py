from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from users.views import CustomLogoutView  
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('webapp.urls')), 
    path('accounts/', include('accounts.urls')), 
    path('logout/', CustomLogoutView.as_view(), name='logout'),  
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
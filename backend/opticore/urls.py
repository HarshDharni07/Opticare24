# Reference: PROMPT.md → System Configuration.
# Purpose: Main URL routing for OptiCare24 API endpoints and admin interface.

"""
URL configuration for OptiCare24 opticore project.

OptiCare24 — Full Stack Optical Shop Management System
Reference: PROMPT.md → Key API Endpoints for all modules
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # Welcome endpoint for testing
    path('', views.welcome_view, name='welcome'),
    
    # Admin interface
    path('admin/', admin.site.urls),
    
    # API endpoints - Reference: PROMPT.md → Frontend ↔ Backend communication over REST
    # Note: Individual app URLs will be included as views are implemented
    # path('api/auth/', include('accounts.urls')),
    # path('api/products/', include('products.urls')),
    # path('api/orders/', include('orders.urls')),
    # path('api/prescriptions/', include('prescriptions.urls')),
    # path('api/warranty/', include('warranty.urls')),
    # path('api/appointments/', include('appointments.urls')),
    # path('api/analytics/', include('analytics.urls')),
]

# Serve media files in development
# Reference: PROMPT.md → Local file system storage for QR codes and uploads
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

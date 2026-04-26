"""
sqli_demo URL Configuration
Routes all requests to the auth_demo app.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('sqli/', include('auth_demo.urls')),
    path('xss/', include('xss_demo.urls')),
    path('upload/', include('upload_demo.urls')),
    path('ai/', include('chatgpt_demo.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

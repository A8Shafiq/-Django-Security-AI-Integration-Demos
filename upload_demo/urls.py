"""
upload_demo URL Configuration

Routes:
    /upload/                     → Dashboard (exploit descriptions + links)
    /upload/vulnerable/          → Vulnerable file upload (no validation)
    /upload/secure/              → Secure file upload (full validation)
    /upload/mitigations/         → Mitigations reference page
"""

from django.urls import path
from . import views

app_name = 'upload_demo'

urlpatterns = [
    path('', views.upload_dashboard, name='dashboard'),
    path('vulnerable/', views.upload_vulnerable, name='vulnerable'),
    path('secure/', views.upload_secure, name='secure'),
    path('mitigations/', views.mitigations, name='mitigations'),
]

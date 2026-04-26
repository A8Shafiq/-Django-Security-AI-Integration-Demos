"""
urls.py — URL routing for auth_demo app

Routes:
    /                   → Login page (both forms)
    /vulnerable-login/  → Vulnerable login endpoint
    /secure-login/      → Secure login endpoint
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_page, name='login_page'),
    path('vulnerable-login/', views.vulnerable_login, name='vulnerable_login'),
    path('secure-login/', views.secure_login, name='secure_login'),
]

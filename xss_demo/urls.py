"""
urls.py — URL routing for xss_demo app

Routes:
    /xss/                        → Dashboard (all 3 XSS types)
    /xss/stored/vulnerable/      → Stored XSS (vulnerable)
    /xss/stored/secure/          → Stored XSS (secure)
    /xss/reflected/vulnerable/   → Reflected XSS (vulnerable)
    /xss/reflected/secure/       → Reflected XSS (secure)
    /xss/dom/                    → DOM-based XSS demo page
"""

from django.urls import path
from . import views

app_name = 'xss_demo'

urlpatterns = [
    path('', views.xss_dashboard, name='dashboard'),

    # Stored XSS
    path('stored/vulnerable/', views.stored_xss_vulnerable, name='stored_vuln'),
    path('stored/secure/', views.stored_xss_secure, name='stored_secure'),

    # Reflected XSS
    path('reflected/vulnerable/', views.reflected_xss_vulnerable, name='reflected_vuln'),
    path('reflected/secure/', views.reflected_xss_secure, name='reflected_secure'),

    # DOM-based XSS
    path('dom/', views.dom_xss, name='dom_xss'),
]

"""
Enhanced URL patterns for core app (domains, niches, audiences).
Includes all the new endpoints we created.
"""

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Domains
    path('domains/', views.list_domains, name='list_domains'),
    
    # Domain-specific data
    path('domains/<str:domain_id>/niches/', views.list_domain_niches, name='domain_niches'),
    path('domains/<str:domain_id>/audiences/', views.list_domain_audiences, name='domain_audiences'),
    path('domains/<str:domain_id>/details/', views.get_domain_details, name='domain_details'),
    
    # User-specific domain data
    path('user/domains/', views.get_user_accessible_domains, name='user_domains'),
    
    # Cache management (staff only)
    path('cache/clear/', views.clear_cache, name='clear_cache'),
]

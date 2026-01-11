"""
URL patterns for books app (book generation and management).
"""

from django.urls import path

from .views import (
    DomainListView,
    BookGenerationStatsView,
    BookGenerationRequestListView,
    BookGenerationRequestDetailView,
    BookGenerationCreateView,
    BookPreviewView,
    BookDownloadView,
    BookDeleteView,
)

app_name = 'books'

urlpatterns = [
    # Domains
    path('domains/', DomainListView.as_view(), name='domains'),

    # User stats
    path('stats/', BookGenerationStatsView.as_view(), name='stats'),

    # Generation requests
    path('generation-requests/', BookGenerationRequestListView.as_view(), name='generation-requests'),
    path('generation-requests/<uuid:generation_request_id>/', BookGenerationRequestDetailView.as_view(), name='generation-request-detail'),

    # Book generation
    path('generate/', BookGenerationCreateView.as_view(), name='generate'),

    # Book actions
    path('<uuid:generation_request_id>/preview/', BookPreviewView.as_view(), name='preview'),
    path('<uuid:generation_request_id>/download/', BookDownloadView.as_view(), name='download'),
    path('<uuid:generation_request_id>/', BookDeleteView.as_view(), name='delete'),
]

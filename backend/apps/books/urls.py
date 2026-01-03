"""
URL patterns for books app (book generation and management).
"""

from django.urls import path

from .views import (
    BookHistoryView,
    BookDetailView,
    BookGenerateView,
)

app_name = 'books'

urlpatterns = [
    path('books/history/', BookHistoryView.as_view(), name='history'),
    path('books/generate/', BookGenerateView.as_view(), name='generate'),
    path('books/<str:book_id>/', BookDetailView.as_view(), name='detail'),
]

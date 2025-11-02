"""
URL patterns for user profile endpoints.
"""

from django.urls import path
from ..views import (
    UserProfileView,
    UserAnalyticsView,
    UserBooksHistoryView,
)

app_name = 'users'

urlpatterns = [
    # User profile
    path('profile/', UserProfileView.as_view(), name='profile'),
    
    # Analytics
    path('analytics/', UserAnalyticsView.as_view(), name='analytics'),
    
    # Books history
    path('books-history/', UserBooksHistoryView.as_view(), name='books_history'),
]

"""
URL patterns for user profile endpoints.
"""

from django.urls import path
from ..views import (
    UserProfileView,
    PasswordChangeView,
    UserAnalyticsView,
    UserBooksHistoryView,
    SubscriptionPlanListView,
    UserUsageView,
)

app_name = 'users'

urlpatterns = [
    # User profile
    path('profile/', UserProfileView.as_view(), name='profile'),
    
    # Password change
    path('change-password/', PasswordChangeView.as_view(), name='change_password'),
    
    # Analytics
    path('analytics/', UserAnalyticsView.as_view(), name='analytics'),
    
    # Books history
    path('books-history/', UserBooksHistoryView.as_view(), name='books_history'),
    
    # Plans and Usage
    path('plans/', SubscriptionPlanListView.as_view(), name='plan_list'),
    path('usage/', UserUsageView.as_view(), name='usage'),
]

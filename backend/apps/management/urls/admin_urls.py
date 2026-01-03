from django.urls import path
from ..views import AdminUserListView, AdminUserDetailView, AdminBookListView, AdminStatsView

app_name = 'management'

urlpatterns = [
    # User management
    path('users/', AdminUserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', AdminUserDetailView.as_view(), name='user_detail'),
    
    # Book management
    path('books/', AdminBookListView.as_view(), name='book_list'),
    
    # Stats
    path('analytics/', AdminStatsView.as_view(), name='analytics'),
]

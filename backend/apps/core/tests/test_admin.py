import pytest
from django.urls import reverse
from rest_framework import status
from apps.users.models import User

class TestAdminDashboard:
    """Test admin management dashboard functionality"""

    def test_admin_user_management_list(self, admin_client):
        """Test admin listing all users"""
        response = admin_client.get(reverse('admin-users'))
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)

    def test_admin_user_detail(self, admin_client, user):
        """Test admin viewing specific user details"""
        response = admin_client.get(reverse('admin-user-detail', kwargs={'pk': user.pk}))
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email

    def test_admin_user_update(self, admin_client, user):
        """Test admin updating user information"""
        data = {
            'first_name': 'AdminUpdated',
            'is_active': False
        }
        response = admin_client.patch(reverse('admin-user-detail', kwargs={'pk': user.pk}), data, format='json')
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.first_name == 'AdminUpdated'
        assert not user.is_active

    def test_admin_user_delete(self, admin_client, user):
        """Test admin deleting a user"""
        response = admin_client.delete(reverse('admin-user-detail', kwargs={'pk': user.pk}))
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not User.objects.filter(pk=user.pk).exists()

    def test_admin_system_analytics(self, admin_client):
        """Test admin viewing system analytics"""
        response = admin_client.get(reverse('admin-analytics'))
        assert response.status_code == status.HTTP_200_OK
        # Check for expected analytics data
        assert 'total_users' in response.data
        assert 'active_users' in response.data
        assert 'total_books' in response.data
        assert 'revenue' in response.data

    def test_admin_books_management(self, admin_client):
        """Test admin managing all books across users"""
        response = admin_client.get(reverse('admin-books'))
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)

    def test_admin_subscription_tracking(self, admin_client):
        """Test admin viewing subscription and revenue tracking"""
        response = admin_client.get(reverse('admin-subscriptions'))
        assert response.status_code == status.HTTP_200_OK
        # Check for subscription data structure
        assert 'active_subscriptions' in response.data
        assert 'revenue_stats' in response.data

    def test_regular_user_cannot_access_admin(self, authenticated_client):
        """Test that regular users cannot access admin endpoints"""
        response = authenticated_client.get(reverse('admin-users'))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_cannot_access_admin(self, api_client):
        """Test that unauthenticated users cannot access admin endpoints"""
        response = api_client.get(reverse('admin-users'))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
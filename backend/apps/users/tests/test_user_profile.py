import pytest
from django.urls import reverse
from rest_framework import status

class TestUserProfile:
    """Test user profile functionality"""

    def test_get_profile(self, authenticated_client, user):
        """Test retrieving user profile"""
        response = authenticated_client.get(reverse('user-profile'))
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email
        assert response.data['first_name'] == user.first_name
        assert response.data['last_name'] == user.last_name

    def test_update_profile(self, authenticated_client, user):
        """Test updating user profile"""
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com'
        }
        response = authenticated_client.put(reverse('user-profile'), data, format='json')
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.first_name == 'Updated'
        assert user.last_name == 'Name'
        assert user.email == 'updated@example.com'

    def test_change_password(self, authenticated_client, user):
        """Test password change"""
        data = {
            'old_password': 'testpass123',
            'new_password': 'newsecurepass123'
        }
        response = authenticated_client.post(reverse('user-change-password'), data, format='json')
        assert response.status_code == status.HTTP_200_OK
        # Verify new password works
        user.refresh_from_db()
        assert user.check_password('newsecurepass123')

    def test_change_password_wrong_old(self, authenticated_client, user):
        """Test password change with wrong old password"""
        data = {
            'old_password': 'wrongpass',
            'new_password': 'newsecurepass123'
        }
        response = authenticated_client.post(reverse('user-change-password'), data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_user_books_history(self, authenticated_client, user):
        """Test retrieving user's books history"""
        response = authenticated_client.get(reverse('user-books'))
        assert response.status_code == status.HTTP_200_OK
        # Assuming books app has this endpoint
        assert isinstance(response.data, list)

    def test_user_analytics(self, authenticated_client, user):
        """Test retrieving user analytics"""
        response = authenticated_client.get(reverse('user-analytics'))
        assert response.status_code == status.HTTP_200_OK
        # Check for expected analytics fields
        assert 'total_books' in response.data
        assert 'usage_stats' in response.data

    def test_subscription_plans(self, authenticated_client, user):
        """Test retrieving available subscription plans"""
        response = authenticated_client.get(reverse('subscription-plans'))
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        # Check for plan structure
        if response.data:
            plan = response.data[0]
            assert 'name' in plan
            assert 'price' in plan
            assert 'features' in plan

    def test_account_deletion(self, authenticated_client, user):
        """Test account deletion"""
        data = {'confirmation': 'DELETE'}
        response = authenticated_client.delete(reverse('user-delete'), data, format='json')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not user.__class__.objects.filter(pk=user.pk).exists()
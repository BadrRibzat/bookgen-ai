import pytest
from django.urls import reverse
from django.core import mail
from rest_framework import status
from apps.users.models import User

class TestAuthentication:
    """Test authentication functionality"""

    def test_user_registration(self, api_client):
        """Test user registration with valid data"""
        data = {
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = api_client.post(reverse('user-register'), data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response.data
        assert 'tokens' in response.data
        assert User.objects.filter(email='newuser@example.com').exists()

    def test_user_login(self, api_client, user):
        """Test user login with correct credentials"""
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = api_client.post(reverse('token_obtain_pair'), data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_user_login_invalid_credentials(self, api_client):
        """Test user login with invalid credentials"""
        data = {
            'email': 'test@example.com',
            'password': 'wrongpass'
        }
        response = api_client.post(reverse('token_obtain_pair'), data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_email_verification(self, api_client, user):
        """Test email verification process"""
        # First, trigger verification email
        response = api_client.post(reverse('user-resend-verification'), {'email': user.email})
        assert response.status_code == status.HTTP_200_OK
        assert len(mail.outbox) == 1

        # Simulate verification (would need token from email)
        # For now, just check email was sent
        email = mail.outbox[0]
        assert 'Verify Your Email' in email.subject
        assert user.email in email.to

    def test_password_reset(self, api_client, user):
        """Test password reset process"""
        # Request password reset
        response = api_client.post(reverse('user-password-reset'), {'email': user.email})
        assert response.status_code == status.HTTP_200_OK
        assert len(mail.outbox) == 1

        # Check email content
        email = mail.outbox[0]
        assert 'Reset Your Password' in email.subject
        assert user.email in email.to

    def test_logout(self, authenticated_client):
        """Test user logout"""
        response = authenticated_client.post(reverse('user-logout'))
        assert response.status_code == status.HTTP_200_OK

    def test_protected_route_access(self, api_client, authenticated_client, user):
        """Test access to protected routes"""
        # Unauthenticated access should fail
        response = api_client.get(reverse('user-profile'))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Authenticated access should succeed
        response = authenticated_client.get(reverse('user-profile'))
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email
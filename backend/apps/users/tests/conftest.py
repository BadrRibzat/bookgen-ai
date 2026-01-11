import pytest
from django.test import Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.users.models import User

@pytest.fixture
def client():
    """Django test client"""
    return Client()

@pytest.fixture
def api_client():
    """DRF API client"""
    return APIClient()

@pytest.fixture
def user():
    """Create a test user"""
    return User.objects.create_user(
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )

@pytest.fixture
def admin_user():
    """Create an admin test user"""
    return User.objects.create_superuser(
        email='admin@example.com',
        password='adminpass123',
        first_name='Admin',
        last_name='User'
    )

@pytest.fixture
def authenticated_client(api_client, user):
    """API client authenticated as regular user"""
    api_client.force_authenticate(user=user)
    return api_client

@pytest.fixture
def admin_client(api_client, admin_user):
    """API client authenticated as admin user"""
    api_client.force_authenticate(user=admin_user)
    return api_client
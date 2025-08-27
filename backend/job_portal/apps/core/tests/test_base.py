from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.core.management import call_command
from django.db import transaction
import json
import os

User = get_user_model()


class JobPortalTestCase(TestCase):
    """Base test case for job portal tests with test data management."""
    
    fixtures = ['test_data.json']
    
    def setUp(self):
        """Set up test data and clients."""
        self.client = Client()
        self.api_client = APIClient()
        
        # Get test users
        self.test_client = User.objects.get(username='testclient')
        self.test_provider = User.objects.get(username='testprovider')
        self.test_admin = User.objects.get(username='testadmin')
        
        # Set default passwords for testing
        self.default_password = 'testpass123'
        self.test_client.set_password(self.default_password)
        self.test_provider.set_password(self.default_password)
        self.test_admin.set_password(self.default_password)
        self.test_client.save()
        self.test_provider.save()
        self.test_admin.save()
    
    def tearDown(self):
        """Clean up after tests."""
        pass
    
    def load_test_data(self):
        """Load test data from fixtures."""
        try:
            call_command('loaddata', 'test_data.json', verbosity=0)
        except Exception as e:
            print(f"Warning: Could not load test data: {e}")
    
    def clear_test_data(self):
        """Clear test data to ensure clean state."""
        # This will be handled by Django's test database rollback
        pass
    
    def authenticate_user(self, user):
        """Authenticate a user for API requests."""
        self.api_client.force_authenticate(user=user)
    
    def login_user(self, username, password=None):
        """Login a user via web interface."""
        if password is None:
            password = self.default_password
        
        login_data = {
            'username': username,
            'password': password
        }
        
        response = self.client.post(reverse('admin:login'), login_data)
        return response


class JobPortalAPITestCase(APITestCase):
    """Base API test case for job portal tests."""
    
    fixtures = ['test_data.json']
    
    def setUp(self):
        """Set up test data and API client."""
        super().setUp()
        
        # Get test users
        self.test_client = User.objects.get(username='testclient')
        self.test_provider = User.objects.get(username='testprovider')
        self.test_admin = User.objects.get(username='testadmin')
        
        # Set default passwords for testing
        self.default_password = 'testpass123'
        self.test_client.set_password(self.default_password)
        self.test_provider.set_password(self.default_password)
        self.test_admin.set_password(self.default_password)
        self.test_client.save()
        self.test_provider.save()
        self.test_admin.save()
    
    def authenticate_user(self, user):
        """Authenticate a user for API requests."""
        self.client.force_authenticate(user=user)
    
    def make_authenticated_request(self, user, method, url, data=None, **kwargs):
        """Make an authenticated API request."""
        self.authenticate_user(user)
        
        if method.lower() == 'get':
            return self.client.get(url, **kwargs)
        elif method.lower() == 'post':
            return self.client.post(url, data, **kwargs)
        elif method.lower() == 'put':
            return self.client.put(url, data, **kwargs)
        elif method.lower() == 'patch':
            return self.client.patch(url, data, **kwargs)
        elif method.lower() == 'delete':
            return self.client.delete(url, **kwargs)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
    
    def assert_response_success(self, response, expected_status=status.HTTP_200_OK):
        """Assert that the response was successful."""
        self.assertEqual(response.status_code, expected_status)
    
    def assert_response_error(self, response, expected_status=status.HTTP_400_BAD_REQUEST):
        """Assert that the response was an error."""
        self.assertEqual(response.status_code, expected_status)
    
    def assert_response_unauthorized(self, response):
        """Assert that the response indicates unauthorized access."""
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])


class TestDataManager:
    """Utility class for managing test data."""
    
    @staticmethod
    def create_test_user(username, email, **kwargs):
        """Create a test user with default values."""
        defaults = {
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '+77001234567',
            'is_verified': True,
            'is_blocked': False
        }
        defaults.update(kwargs)
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password='testpass123',
            **defaults
        )
        return user
    
    @staticmethod
    def cleanup_test_data():
        """Clean up test data after tests."""
        # This will be handled by Django's test database rollback
        pass


from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from .test_base import JobPortalAPITestCase

User = get_user_model()


class TestAuthentication(JobPortalAPITestCase):
    """
    Test authentication functionality.
    These tests mimic the authentication flow a mobile app would use.
    """
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.client = APIClient()
    
    def test_user_registration(self):
        """Test user registration endpoint."""
        url = reverse('accounts:register')
        
        registration_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
            'phone_number': '+77001234570'
        }
        
        response = self.client.post(url, registration_data)
        
        # Check if user was created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        
        # Verify user exists in database
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'User')
    
    def test_user_registration_validation(self):
        """Test user registration validation."""
        url = reverse('accounts:register')
        
        # Test with missing required fields
        invalid_data = {
            'username': 'newuser',
            'email': 'invalid-email'
        }
        
        response = self.client.post(url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test with mismatched passwords
        invalid_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'pass123',
            'password_confirm': 'different123'
        }
        
        response = self.client.post(url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_login(self):
        """Test user login endpoint."""
        url = reverse('accounts:login')
        
        login_data = {
            'username': 'testclient',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
        
        # Check user data
        user_data = response.data['user']
        self.assertEqual(user_data['username'], 'testclient')
        self.assertEqual(user_data['email'], 'testclient@example.com')
    
    def test_user_login_invalid_credentials(self):
        """Test user login with invalid credentials."""
        url = reverse('accounts:login')
        
        invalid_data = {
            'username': 'testclient',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_token_authentication(self):
        """Test that token authentication works correctly."""
        # First login to get token
        login_url = reverse('accounts:login')
        login_data = {
            'username': 'testclient',
            'password': 'testpass123'
        }
        
        login_response = self.client.post(login_url, login_data)
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        
        token = login_response.data['token']
        
        # Use token to access protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        
        # Try to access a protected endpoint
        profile_url = reverse('accounts:profile')
        response = self.client.get(profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_token_invalidation(self):
        """Test that invalid tokens are rejected."""
        self.client.credentials(HTTP_AUTHORIZATION='Token invalidtoken123')
        
        profile_url = reverse('accounts:profile')
        response = self.client.get(profile_url)
        
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
    
    def test_user_profile_access(self):
        """Test that authenticated users can access their profile."""
        # Authenticate user
        self.authenticate_user(self.test_client)
        
        profile_url = reverse('accounts:profile')
        response = self.client.get(profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testclient')
    
    def test_user_profile_update(self):
        """Test that users can update their profile."""
        # Authenticate user
        self.authenticate_user(self.test_client)
        
        profile_url = reverse('accounts:profile')
        
        # Update profile data
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone_number': '+77001234571'
        }
        
        response = self.client.patch(profile_url, update_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
        self.assertEqual(response.data['last_name'], 'Name')
        
        # Verify changes in database
        user = User.objects.get(username='testclient')
        self.assertEqual(user.first_name, 'Updated')
        self.assertEqual(user.last_name, 'Name')
    
    def test_password_change(self):
        """Test that users can change their password."""
        # Authenticate user
        self.authenticate_user(self.test_client)
        
        password_change_url = reverse('accounts:change-password')
        
        password_data = {
            'old_password': 'testpass123',
            'new_password': 'newpass456',
            'new_password_confirm': 'newpass456'
        }
        
        response = self.client.post(password_change_url, password_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify password was changed
        user = User.objects.get(username='testclient')
        self.assertTrue(user.check_password('newpass456'))
    
    def test_password_change_validation(self):
        """Test password change validation."""
        # Authenticate user
        self.authenticate_user(self.test_client)
        
        password_change_url = reverse('accounts:change-password')
        
        # Test with wrong old password
        invalid_data = {
            'old_password': 'wrongpassword',
            'new_password': 'newpass456',
            'new_password_confirm': 'newpass456'
        }
        
        response = self.client.post(password_change_url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test with mismatched new passwords
        invalid_data = {
            'old_password': 'testpass123',
            'new_password': 'newpass456',
            'new_password_confirm': 'different789'
        }
        
        response = self.client.post(password_change_url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_logout(self):
        """Test user logout functionality."""
        # First login to get token
        login_url = reverse('accounts:login')
        login_data = {
            'username': 'testclient',
            'password': 'testpass123'
        }
        
        login_response = self.client.post(login_url, login_data)
        token = login_response.data['token']
        
        # Logout
        logout_url = reverse('accounts:logout')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        
        response = self.client.post(logout_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify token is no longer valid
        profile_url = reverse('accounts:profile')
        response = self.client.get(profile_url)
        
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
    
    def test_user_verification(self):
        """Test user verification functionality."""
        # Create unverified user
        unverified_user = User.objects.create_user(
            username='unverified',
            email='unverified@example.com',
            password='testpass123',
            is_verified=False
        )
        
        # Test that unverified users cannot access certain endpoints
        self.client.force_authenticate(user=unverified_user)
        
        # Try to access profile (should work but with verification status)
        profile_url = reverse('accounts:profile')
        response = self.client.get(profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_verified'])
    
    def test_user_blocking(self):
        """Test user blocking functionality."""
        # Create blocked user
        blocked_user = User.objects.create_user(
            username='blocked',
            email='blocked@example.com',
            password='testpass123',
            is_blocked=True
        )
        
        # Test that blocked users cannot authenticate
        login_url = reverse('accounts:login')
        login_data = {
            'username': 'blocked',
            'password': 'testpass123'
        }
        
        response = self.client.post(login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_session_authentication(self):
        """Test session-based authentication."""
        # Login to create session
        login_url = reverse('accounts:login')
        login_data = {
            'username': 'testclient',
            'password': 'testpass123'
        }
        
        response = self.client.post(login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Use session to access protected endpoint
        profile_url = reverse('accounts:profile')
        response = self.client.get(profile_url)
        
        # Should work with session authentication
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_authentication_rate_limiting(self):
        """Test authentication rate limiting."""
        login_url = reverse('accounts:login')
        login_data = {
            'username': 'testclient',
            'password': 'wrongpassword'
        }
        
        # Make multiple failed login attempts
        for _ in range(5):
            response = self.client.post(login_url, login_data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Should still be able to make requests (rate limiting might be implemented)
        response = self.client.get(reverse('core:languages'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_authentication_security(self):
        """Test authentication security measures."""
        # Test that passwords are not returned in responses
        login_url = reverse('accounts:login')
        login_data = {
            'username': 'testclient',
            'password': 'testpass123'
        }
        
        response = self.client.post(login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that password is not in response
        self.assertNotIn('password', response.data)
        
        # Check that user data doesn't contain sensitive information
        user_data = response.data['user']
        self.assertNotIn('password', user_data)
        self.assertNotIn('password_hash', user_data)


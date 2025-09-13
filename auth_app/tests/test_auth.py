"""Test suite for authentication and profile management endpoints.

Covers:
- User registration
- User login
- Profile retrieval, update, and list endpoints
"""

from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from .utils import (
    create_test_image_file,
    create_test_user,
    create_test_users_token,
    create_test_users_profile,
    first_name,
    last_name,
    image_name,
    username
)




class RegistrationTests(APITestCase):
    """Test cases for user registration."""

    def setUp(self):
        """Set up default registration data."""
        self.url = reverse('registration')
        self.username = "TestUser"
        self.data = {
            "username": self.username,
            "email": "test@user.de",
            "password": "examplePassword",
            "repeated_password": "examplePassword",
            "type": "customer"
        }


    def test_post_success(self):
        """Test successful user registration."""
        response = self.client.post(self.url, self.data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)
        self.assertEqual(response.data['username'], self.data['username'])
        self.assertEqual(response.data['email'], self.data['email'])
        self.assertNotIn('password', response.data)

        user = User.objects.get(username=self.username)
        token = Token.objects.get(user=user)

        self.assertEqual(token.key, response.data['token'])


    def test_post_duplicate_fails(self):
        """Test that registration with duplicate data fails (400)."""
        self.client.post(self.url, self.data, format='json')
        response = self.client.post(self.url, self.data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_post_fails_password_mismatch(self):
        data = {
            "username": self.username,
            "email": "test@user.de",
            "password": "examplePassword",
            "repeated_password": "WRONG",
            "type": "customer"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_post_fails_missing_fields_or_wrong_type(self):
        for data in [
            {"email": "test@user.de", "password": "examplePassword", "repeated_password": "examplePassword", "type": "customer"},
            {"username": self.username, "password": "examplePassword", "repeated_password": "examplePassword", "type": "customer"},
            {"username": self.username, "email": "test@user.de", "repeated_password": "examplePassword", "type": "customer"},
            {"username": self.username, "email": "test@user.de", "password": "examplePassword", "type": "customer"},
            {"username": self.username, "email": "test@user.de", "password": "examplePassword", "repeated_password": "examplePassword", "type": "WRONG"},
        ]:
            response = self.client.post(self.url, data, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



class LoginTests(APITestCase):
    """Test cases for user login."""

    def setUp(self):
        """Create a test user and token for login tests."""
        self.username = "exampleUsername"
        self.password = "examplePassword"
        self.email = "example@mail.de"
        self.user = User.objects.create_user(username=self.username, password=self.password, email=self.email)
        self.token = Token.objects.create(user=self.user)
        self.url = reverse('login')


    def test_post_success(self):
        """Test successful login with correct credentials."""
        data = {
            "username": self.username,
            "password": self.password
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.token.key, response.data['token'])
        self.assertEqual(self.user.id, response.data['user_id'])
        self.assertEqual(self.username, response.data['username'])
        self.assertEqual(self.email, response.data['email'])
        self.assertNotIn('password', response.data)


    def test_post_fails_user_not_exists_or_wrong_password(self):
        """Test login fails with non-existent username or incorrect password."""
        for data in [
            {"username": "WRONG", "password": self.password},
            {"username": self.username, "password": "WRONG"},
        ]:
            response = self.client.post(self.url, data, format='json')

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProfileTests(APITestCase):
    """Test cases for profile endpoints."""

    def setUp(self):
        """Create test users, tokens, and profiles."""
        self.url_business = reverse('profile_business-list')
        self.url_customer = reverse('profile_customer-list')
        self.patch_data = {
            "first_name": "Max",
            "last_name": "Mustermann",
            "location": "Berlin",
            "tel": "+49531697151",
            "description": "Updated business description",
            "working_hours": "10-18",
            "email": "new_email@business.de",
            "file": create_test_image_file()
        }
        self.user = create_test_user()
        self.token = create_test_users_token(self.user)
        self.profile = create_test_users_profile(self.user)
        self.url_detail = reverse('profile-detail', kwargs={'pk': self.profile.pk})
        self.second_user = create_test_user(username='Test2', password='Test12§$', email="example2@mail.de")
        self.second_token = create_test_users_token(self.second_user)
        self.second_profile = create_test_users_profile(self.second_user, 'customer')


    def test_get_detail_success(self):
        """Test retrieving profile detail succeeds with authentication."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        response = self.client.get(self.url_detail)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.user.id)
        self.assertEqual(response.data['username'], username)
        self.assertIsInstance(response.data['first_name'], str, msg='First name is not a string!')
        self.assertIsInstance(response.data['last_name'], str, msg='Last name is not a string!')
        self.assertEqual(response.data['first_name'], first_name)
        self.assertEqual(response.data['last_name'], last_name)
        self.assertIn(image_name.split('.')[0], response.data['file'])
        self.assertIsInstance(response.data['location'], str, msg='Location name is not a string!')
        self.assertIn('tel', response.data)
        self.assertIsInstance(response.data['description'], str, msg='Description is not a string!')
        self.assertIsInstance(response.data['working_hours'], str, msg='Working_hours is not a string!')
        self.assertEqual(response.data['type'], self.profile.type)
        self.assertIsInstance(response.data['created_at'], str, msg='Created_at is not a string!')


    def test_get_detail_fails_not_authorized(self):
        """Test retrieving profile detail fails without authentication."""
        response = self.client.get(self.url_detail)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_get_detail_fails_user_not_exists(self):
        """Test retrieving profile detail fails for non-existent user."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        url = reverse('profile-detail', kwargs={'pk': 9999})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_patch_detail_success(self):
        """Test successfully updating profile with PATCH request."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        response = self.client.patch(self.url_detail, self.patch_data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.user.id)
        self.assertEqual(response.data['username'], username)
        self.assertEqual(response.data['first_name'], self.patch_data['first_name'])
        self.assertEqual(response.data['last_name'], self.patch_data['last_name'])
        self.assertEqual(response.data['location'], self.patch_data['location'])
        self.assertEqual(response.data['tel'], self.patch_data['tel'])
        self.assertEqual(response.data['description'], self.patch_data['description'])
        self.assertEqual(response.data['working_hours'], self.patch_data['working_hours'])
        self.assertEqual(response.data['email'], self.patch_data['email'])
        self.assertEqual(response.data['type'], self.profile.type)
        self.assertIn('test_image', response.data['file'])
        self.assertIsInstance(response.data['created_at'], str, msg='First name is not a string!')


    def test_patch_detail_fails_not_authorized(self):
        """Test updating profile fails without authentication."""
        response = self.client.patch(self.url_detail, self.patch_data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_patch_detail_fails_user_not_owner(self):
        """Test updating profile fails when user is not the owner."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.second_token.key)

        response = self.client.patch(self.url_detail, self.patch_data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    
    def test_patch_detail_fails_user_not_exists(self):
        """Test updating profile fails for non-existent user."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        url = reverse('profile-detail', kwargs={'pk': 9999})

        response = self.client.patch(url, self.patch_data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_get_list_business_success(self):
        """Test retrieving business profile list succeeds with authentication."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        expected_fields = {
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
        }

        response = self.client.get(self.url_business)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data:
            self.assertEqual(set(item.keys()), expected_fields)


    def test_get_list_business_fails_not_authorized(self):
        """Test retrieving business profile list fails without authentication."""
        response = self.client.get(self.url_business)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_get_list_customer_success(self):
        """Test retrieving customer profile list succeeds with authentication."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        expected_fields = {
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "uploaded_at",
            "type",
        }

        response = self.client.get(self.url_customer)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data:
            self.assertEqual(set(item.keys()), expected_fields)


    def test_get_list_customer_fails_not_authorized(self):
        """Test retrieving customer profile list fails without authentication."""
        response = self.client.get(self.url_customer)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
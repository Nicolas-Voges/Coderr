from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework.authtoken.models import Token
from auth_app.models import Profile

class RegistrationTests(APITestCase):

    def setUp(self):
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
        response = self.client.post(self.url, self.data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)
        self.assertEqual(response.data['username'], self.data['username'])
        self.assertEqual(response.data['email'], self.data['email'])

        user = User.objects.get(username=self.username)
        token = Token.objects.get(user=user)

        self.assertEqual(token.key, response.data['token'])


    def test_post_duplicate_fails(self):
        self.client.post(self.url, self.data, format='json')
        response = self.client.post(self.url, self.data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(APITestCase):

    def setUp(self):
        self.username = "exampleUsername"
        self.password = "examplePassword"
        self.email = "example@mail.de"
        self.user = User.objects.create_user(username=self.username, password=self.password, email=self.email)
        self.token = Token.objects.create(user=self.user)
        self.url = reverse('login')


    def test_post_success(self):
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


    def test_post_fails_user_not_exists(self):
        data = {
            "username": 'WRONG',
            "password": self.password
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_post_fails_wrong_password(self):
        data = {
            "username": self.username,
            "password": 'WRONG'
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProfileTests(APITestCase):

    def setUp(self):
        self.url_business = reverse('profile_business-list')
        self.url_customer = reverse('profile_customer-list')
        self.username = "exampleUsername"
        self.password = "examplePassword"
        self.email = "example@mail.de"
        self.first_name = 'Max'
        self.last_name = ''
        self.image_name = "test_image.jpg"
        self.image = SimpleUploadedFile(
            name=self.image_name,
            content=b"fake image content",
            content_type="image/jpeg"
        )
        self.patch_data = {
            "first_name": "Max",
            "last_name": "Mustermann",
            "location": "Berlin",
            "tel": "987654321",
            "description": "Updated business description",
            "working_hours": "10-18",
            "email": "new_email@business.de",
            "file": self.image
        }
        self.user = User.objects.create_user(username=self.username,
                                             password=self.password,
                                             email=self.email,
                                             first_name=self.first_name,
                                             last_name=self.last_name)
        self.token = Token.objects.create(user=self.user)
        self.profile = Profile.objects.create(
            user=self.user,
            file=self.image,
            location="Berlin",
            tel="123456789",
            description="Business description",
            working_hours="9-17",
            type="business",
            email=self.email,
            created_at=timezone.now()
        )
        self.url_detail = reverse('profile-detail', kwargs={'pk': self.profile.pk})


    def test_get_detail_success(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        response = self.client.get(self.url_detail)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.user.id)
        self.assertEqual(response.data['username'], self.username)
        self.assertIsInstance(response.data['first_name'], str, msg='First name is not a string!')
        self.assertIsInstance(response.data['last_name'], str, msg='Last name is not a string!')
        self.assertEqual(response.data['first_name'], self.first_name)
        self.assertEqual(response.data['last_name'], self.last_name)
        self.assertIn(self.image_name.split('.')[0], response.data['file'])
        self.assertIsInstance(response.data['location'], str, msg='Location name is not a string!')
        self.assertIn('tel', response.data)
        self.assertIsInstance(response.data['description'], str, msg='Description is not a string!')
        self.assertIsInstance(response.data['working_hours'], str, msg='Working_hours is not a string!')
        self.assertEqual(response.data['type'], self.profile.type)
        self.assertEqual(response.data['email'], self.email)
        self.assertEqual(response.data['email'], self.email)
        self.assertIsInstance(response.data['created_at'], str, msg='Created_at is not a string!')


    def test_get_detail_fails_not_authorized(self):
        response = self.client.get(self.url_detail)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_get_detail_fails_user_not_exists(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        url = reverse('profile-detail', kwargs={'pk': 9999})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_patch_detail_success(self):
        
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        response = self.client.patch(self.url_detail, self.patch_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.user.id)
        self.assertEqual(response.data['username'], self.username)
        self.assertEqual(response.data['first_name'], self.patch_data['first_name'])
        self.assertEqual(response.data['last_name'], self.patch_data['last_name'])
        self.assertEqual(response.data['location'], self.patch_data['location'])
        self.assertEqual(response.data['tel'], self.patch_data['tel'])
        self.assertEqual(response.data['description'], self.patch_data['description'])
        self.assertEqual(response.data['working_hours'], self.patch_data['working_hours'])
        self.assertEqual(response.data['email'], self.patch_data['email'])
        self.assertEqual(response.data['type'], self.profile.type)
        self.assertTrue(response.data['file'].name.endswith(self.image_name))
        self.assertIsInstance(response.data['created_at'], str, msg='First name is not a string!')


    def test_patch_detail_fails_not_authorized(self):
        response = self.client.patch(self.url_detail, self.patch_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_patch_detail_fails_user_not_owner(self):
        second_user = User.objects.create_user(username='Test2', password='Test12§$')
        second_token = Token.objects.create(user=second_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + second_token.key)

        response = self.client.patch(self.url_detail, self.patch_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    
    def test_patch_detail_fails_user_not_exists(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        url = reverse('profile-detail', kwargs={'pk': 9999})

        response = self.client.patch(url, self.patch_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
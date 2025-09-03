from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
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
        self.url_detail = reverse('profile-detail')
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
        self.user = User.objects.create_user(username=self.username,
                                             password=self.password,
                                             email=self.email,
                                             first_name=self.first_name,
                                             last_name=self.last_name)
        self.token = Token.objects.create(user=self.user)
        self.profile = Profile.objects.create(
            user=self.user.id,
            username=self.username,
            first_name=self.first_name,
            last_name=self.last_name,
            file=self.image,
            location="Berlin",
            tel="123456789",
            description="Business description",
            working_hours="9-17",
            type="business",
            email=self.email,
        )


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
        self.assertTrue(response.data['file'].name.endswith(self.image_name))
        self.assertIsInstance(response.data['location'], str, msg='Location name is not a string!')
        self.assertIn('tel', response.data)
        self.assertIsInstance(response.data['description'], str, msg='Description is not a string!')
        self.assertIsInstance(response.data['working_hours'], str, msg='Working_hours is not a string!')
        self.assertEqual(response.data['type'], self.profile.type)
        self.assertEqual(response.data['email'], self.email)
        self.assertEqual(response.data['email'], self.email)
        self.assertIsInstance(response.data['create_at'], str, msg='Create_at is not a string!')


    def test_get_detail_fails_not_authorized(self):
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


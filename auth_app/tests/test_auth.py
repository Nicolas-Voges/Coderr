from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

class RegistrationTests(APITestCase):       

    def test_registration_post(self):
        url = reverse('registration')
        data = {
            "username": "TestUser",
            "email": "test@user.de",
            "password": "examplePassword",
            "repeated_password": "examplePassword",
            "type": "customer"
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)
        self.assertEqual(response.data['username'], data['username'])
        self.assertEqual(response.data['email'], data['email'])

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTest(APITestCase):

    def setUp(self):
        self.username = "exampleUsername"
        self.password = "examplePassword"
        self.email = "example@mail.de"
        self.user = User.objects.create_user(username=self.username, password=self.password, email=self.email)
        self.token = Token.objects.create(user=self.user)
        self.url = reverse('login')



    def test_login_post(self):
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
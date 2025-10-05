from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.tests.utils import (
    create_test_image_file,
    create_test_user,
    create_test_users_token,
    create_test_users_profile,
    delete_test_images
    )
from coderr_app.models import Order
from .utils import create_offer, create_detail_set

class OrdersTests(APITestCase):

    def setUp(self):
        self.expected_fields = {
            "id",
            "customer_user",
            "business_user",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
            "status",
            "created_at",
            "updated_at"
        }
        self.user_business = create_test_user()
        self.token_business = create_test_users_token(self.user_business)
        self.profile_business = create_test_users_profile(self.user_business)
        self.user_customer = create_test_user(username='customer')
        self.token_customer = create_test_users_token(self.user_customer)
        self.profile_customer = create_test_users_profile(self.user_customer, 'customer')
        self.user_admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123')
        self.token_admin = create_test_users_token(self.user_admin)
        self.profile_customer = create_test_users_profile(self.user_admin)
        self.offer = create_offer(self.user_business)
        self.detail_basic, self.detail_standard, self.detail_premium = create_detail_set(self.offer.id)
        self.order = Order.objects.create(
            offer_detail=self.detail_basic,
            customer_user=self.user_customer,
            business_user=self.user_business,
            status='in_progress',
            created_at=timezone.now(),
            updated_at=None
        )
        self.url_list = reverse('orders-list')
        self.url_detail = reverse('orders-detail', kwargs={'pk': self.order.pk})
        self.post_request_body = {
            'offer_detail_id': self.detail_basic.id
        }
        self.patch_request_body = {
            'status': 'completed'
        }


    def tearDown(self):
        delete_test_images()


    def test_post_success(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_customer.key)

        response = self.client.post(self.url_list, self.post_request_body, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(set(response.data.keys()), self.expected_fields)
        self.assertEqual(response.data['customer_user'], self.user_customer.id)
        self.assertEqual(response.data['business_user'], self.user_business.id)
        self.assertTrue(Order.objects.filter(offer_detail_id=self.detail_basic.id).exists())


    def test_post_fails(self):
        wrong_data = {
            "offer_detail_id": 'ä'
        }
        not_existing_data = {
            "offer_detail_id": 99999
        }
        cases = [
            (None, self.post_request_body, status.HTTP_401_UNAUTHORIZED), 
            (self.token_business, self.post_request_body, status.HTTP_403_FORBIDDEN),
            (self.token_customer, wrong_data, status.HTTP_400_BAD_REQUEST),
            (self.token_customer, not_existing_data, status.HTTP_404_NOT_FOUND)
        ]
        for token, data, expected in cases:
            if token:
                self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
            response = self.client.post(self.url_list, data, format='json')
            self.assertEqual(response.status_code, expected)


    def test_get_list_success(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_business.key)
        response = self.client.get(self.url_list)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data[0].keys()), self.expected_fields)
        self.assertIsInstance(response.data[0]['features'], list)


    def test_get_list_fails(self):
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_patch_success(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_business.key)
        response = self.client.patch(self.url_detail, self.patch_request_body, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), self.expected_fields)
        self.assertEqual(response.data['status'], 'completed')


    def test_patch_fails(self):
        wrong_data = {
            'status': 'done'
        }
        cases = [
            (self.url_detail, None, self.patch_request_body, status.HTTP_401_UNAUTHORIZED), 
            (self.url_detail, self.token_customer, self.patch_request_body, status.HTTP_403_FORBIDDEN),
            (self.url_detail, self.token_business, wrong_data, status.HTTP_400_BAD_REQUEST),
            (reverse('orders-detail', kwargs={'pk': 99999}), self.token_business, self.patch_request_body, status.HTTP_404_NOT_FOUND)
        ]
        for url, token, data, expected in cases:
            if token:
                self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
            response = self.client.patch(url, data, format='json')
            self.assertEqual(response.status_code, expected)


    def test_delete(self):
        cases = [
            (None, status.HTTP_401_UNAUTHORIZED),
            (self.token_business, status.HTTP_403_FORBIDDEN),
            (self.token_customer, status.HTTP_403_FORBIDDEN),
            (self.token_admin, status.HTTP_204_NO_CONTENT),
            (self.token_admin, status.HTTP_404_NOT_FOUND)
        ]
        for token, expected in cases:
            if token:
                self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
            response = self.client.delete(self.url_detail)
            self.assertEqual(response.status_code, expected)


    def test_get_detail_in_progress_success(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_business.key)
        response = self.client.get(reverse('orders-detail-in_progress', kwargs={'pk': self.user_business.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order_count'], 1)


    def test_get_detail_in_progress_fails(self):
        response = self.client.get(reverse('orders-detail-in_progress', kwargs={'pk': self.user_business.id}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_business.key)
        response = self.client.get(reverse('orders-detail-in_progress', kwargs={'pk': 99999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
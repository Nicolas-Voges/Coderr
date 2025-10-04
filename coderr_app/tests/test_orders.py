from django.urls import reverse
from django.utils import timezone

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
        self.offer = create_offer(self.user_business)
        self.detail_basic, self.detail_standard, self.detail_premium = create_detail_set(self.offer.id)
        self.order = Order.objects.create(
            offer_detail_id=self.offer.id,
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
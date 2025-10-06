"""
Integration test for the `base_info` endpoint.

Verifies aggregated statistics such as review count, average rating,
business profile count, and offer count.
"""

from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.tests.utils import (
    create_test_user,
    create_test_users_token,
    create_test_users_profile,
    delete_test_images
)
from coderr_app.models import Review
from .utils import create_offer

class base_info_tests(APITestCase):
    """Test suite for the base info endpoint."""
    
    def setUp(self):
        """Prepare users, tokens, profiles, offers, and reviews."""

        #Business users
        self.user_business = create_test_user()
        self.token_business = create_test_users_token(self.user_business)
        self.profile_business = create_test_users_profile(self.user_business)

        self.user_business_2 = create_test_user(username='Review Tester', email='k@k.kk')
        self.token_business_2 = create_test_users_token(self.user_business_2)
        self.profile_business_2 = create_test_users_profile(self.user_business_2)

        #Customer users
        self.user_customer = create_test_user(username='customer')
        self.token_customer = create_test_users_token(self.user_customer)
        self.profile_customer = create_test_users_profile(self.user_customer, 'customer')

        self.user_customer_2 = create_test_user(username='customer2')
        self.token_customer_2 = create_test_users_token(self.user_customer_2)
        self.profile_customer_2 = create_test_users_profile(self.user_customer_2, 'customer')

        # Offer and Review setup
        self.offer = create_offer(self.user_business)
        self.review = Review.objects.create(
            business_user=self.user_business,
            reviewer=self.user_customer,
            rating=4,
            description='Test!',
            created_at=timezone.now()
        )
        self.review_2 = Review.objects.create(
            business_user=self.user_business,
            reviewer=self.user_customer_2,
            rating=2,
            description='Test 2!',
            created_at=timezone.now()
        )


    def tearDown(self):
        """Delete all test images after running a test."""
        delete_test_images()


    def test_base_info(self):
        """Ensure the endpoint returns correct global statistics."""
        excepted_fields = {
            "review_count",
            "average_rating",
            "business_profile_count",
            "offer_count"
        }
        response = self.client.get(reverse('base_info'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), excepted_fields)
        self.assertEqual(response.data['review_count'], 2)
        self.assertIsInstance(response.data['review_count'], int)
        self.assertEqual(response.data['average_rating'], 3)
        self.assertIsInstance(response.data['average_rating'], float)
        self.assertEqual(response.data['business_profile_count'], 2)
        self.assertIsInstance(response.data['business_profile_count'], int)
        self.assertEqual(response.data['offer_count'], 1)
        self.assertIsInstance(response.data['offer_count'], int)
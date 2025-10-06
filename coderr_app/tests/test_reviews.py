"""
Automated API tests for the Review endpoints.

Covers CRUD operations, permissions, and filtering behavior for reviews.
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

class ReviewsTests(APITestCase):
    """Integration tests for the Review API."""

    def setUp(self):
        """Create test users, profiles, tokens, and an initial review."""
        self.expected_fields = {
            'id',
            'business_user',
            'reviewer',
            'rating',
            'description',
            'created_at',
            'updated_at'
        }

        # Business users
        self.user_business = create_test_user()
        self.token_business = create_test_users_token(self.user_business)
        self.profile_business = create_test_users_profile(self.user_business)

        self.user_business_2 = create_test_user(username='Review Tester', email='k@k.kk')
        self.token_business_2 = create_test_users_token(self.user_business_2)
        self.profile_business_2 = create_test_users_profile(self.user_business_2)

        # Customer users
        self.user_customer = create_test_user(username='customer')
        self.token_customer = create_test_users_token(self.user_customer)
        self.profile_customer = create_test_users_profile(self.user_customer, 'customer')

        self.user_customer_2 = create_test_user(username='customer_2')
        self.token_customer_2 = create_test_users_token(self.user_customer_2)
        self.profile_customer_2 = create_test_users_profile(self.user_customer_2, 'customer')

        # Initial review
        self.review = Review.objects.create(
            business_user=self.user_business,
            reviewer=self.user_customer,
            rating=4,
            description='Test!',
            created_at=timezone.now()
        )

        # Common URLs and payloads
        self.url_list = reverse('reviews-list')
        self.url_detail = reverse('reviews-detail', kwargs={'pk': self.review.pk})
        self.post_request_body = {
            "business_user": self.user_business_2.pk,
            "rating": 2,
            "description": "Post test!"
        }
        self.patch_request_body = {
              "rating": 5,
              "description": "Noch besser als erwartet!"
        }
        

    def tearDown(self):
        """Clean up created image files."""
        delete_test_images()


    def test_post_success(self):
        """Customer can successfully post a new review."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_customer.key)
        response = self.client.post(self.url_list, self.post_request_body, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['reviewer'], self.user_customer.pk)
        self.assertEqual(response.data['description'], self.post_request_body['description'])
        self.assertIsInstance(response.data['rating'], int)
        self.assertEqual(set(response.data.keys()), self.expected_fields)
        self.assertEqual(response.data['updated_at'], None)


    def test_post_fails(self):
        """Posting reviews fails for invalid data or unauthorized users."""
        wrong_data = {
            "business_user": self.user_business.pk,
            "rating": 4,
            "description": "Duplicate!"
        }
        cases = [
            (None, self.post_request_body, status.HTTP_401_UNAUTHORIZED), 
            (self.token_business, self.post_request_body, status.HTTP_403_FORBIDDEN),
            (self.token_customer, wrong_data, status.HTTP_400_BAD_REQUEST)
        ]
        for token, data, expected in cases:
            if token:
                self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
            response = self.client.post(self.url_list, data, format='json')
            self.assertEqual(response.status_code, expected)


    def test_get_list_success(self):
        """Authorized users can list and filter reviews."""

        # Create additional reviews
        Review.objects.create(
            business_user=self.user_business,
            reviewer=self.user_customer_2,
            rating=1,
            description='Test!',
            created_at=timezone.now()
        )
        Review.objects.create(
            business_user=self.user_business_2,
            reviewer=self.user_customer,
            rating=3,
            description='Test!',
            created_at=timezone.now()
        )
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_business.key)
        response = self.client.get(self.url_list)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data[0].keys()), self.expected_fields)

        # Filtering & ordering tests
        param_tests = [
            ({'business_user_id': self.user_business.pk}, lambda reviews: all(review['business_user'] == self.user_business.pk for review in reviews), 2),
            ({'reviewer_id': self.user_customer.pk}, lambda reviews: all(review['reviewer'] <= self.user_customer.pk for review in reviews), 2),
            ({'ordering': 'rating'}, lambda reviews: [review['rating'] for review in reviews] == sorted([review['rating'] for review in reviews]), 3),
            ({'ordering': 'created_at'}, lambda reviews: [review['created_at'] for review in reviews] == sorted([review['created_at'] for review in reviews]), 3)
        ]

        for params, check, lenght in param_tests:
            response = self.client.get(self.url_list, params)
            reviews = response.data
            self.assertEqual(len(reviews), lenght, f"Param test returned no offers for params: {params}")
            self.assertTrue(check(reviews))

    
    def test_get_list_fails(self):
        """Unauthenticated users cannot retrieve the review list."""
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_delete(self):
        """Only the reviewer can delete their own review."""
        cases = [
            (None, status.HTTP_401_UNAUTHORIZED),
            (self.token_business, status.HTTP_403_FORBIDDEN),
            (self.token_customer, status.HTTP_204_NO_CONTENT),
            (self.token_customer, status.HTTP_404_NOT_FOUND)
        ]
        for token, expected in cases:
            if token:
                self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
            response = self.client.delete(self.url_detail)
            self.assertEqual(response.status_code, expected)


    def test_patch_success(self):
        """Reviewer can successfully update their review."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_customer.key)
        response = self.client.patch(self.url_detail, self.patch_request_body, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), self.expected_fields)
        self.assertEqual(response.data['rating'], self.patch_request_body['rating'])
        self.assertEqual(response.data['description'], self.patch_request_body['description'])
        self.assertEqual(response.data['reviewer'], self.user_customer.pk)
        self.assertEqual(response.data['business_user'], self.user_business.pk)
        self.assertIsInstance(response.data['updated_at'], str)


    def test_patch_fails(self):
        """Patch requests fail for invalid data, unauthorized, or non-existing reviews."""
        wrong_data = {
            'rating': '5u'
        }
        cases = [
            (self.url_detail, None, self.patch_request_body, status.HTTP_401_UNAUTHORIZED), 
            (self.url_detail, self.token_business, self.patch_request_body, status.HTTP_403_FORBIDDEN),
            (self.url_detail, self.token_customer, wrong_data, status.HTTP_400_BAD_REQUEST),
            (reverse('reviews-detail', kwargs={'pk': 99999}), self.token_customer, self.patch_request_body, status.HTTP_404_NOT_FOUND)
        ]
        for url, token, data, expected in cases:
            if token:
                self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
            response = self.client.patch(url, data, format='json')
            self.assertEqual(response.status_code, expected)
"""
Django REST Framework integration tests for Offer and Detail endpoints.

Includes:
- Authentication and permission checks
- CRUD operations on Offer and Detail
- Query parameter tests (filtering, ordering, searching, pagination)
- Validation of request and response data
"""

import copy
# from decimal import Decimal

from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.tests.utils import (
    create_test_image_file,
    create_test_user,
    create_test_users_token,
    create_test_users_profile
    )
from coderr_app.models import Offer, Detail

class OffersTests(APITestCase):
    """
    Integration tests for Offer and Detail API endpoints.
    Covers CRUD operations, authentication, permissions,
    filtering, ordering, and validation cases.
    """
        
    def create_offer(self, user):
        """
        Helper method to create an Offer with default test data.
        """
        return Offer.objects.create(
            user=user,
            title='Testtitle',
            image=create_test_image_file(),
            description="Test",
            created_at=timezone.now()
            # details=self.post_request_body['details']
        )


    def setUp(self):
        """
        Create test users, profiles, tokens, and initial Offer/Detail objects.
        Runs before each test case.
        """
        self.user = create_test_user()
        self.token = create_test_users_token(self.user)
        self.profile = create_test_users_profile(self.user)
        self.second_user = create_test_user(username='Test2', password='Test12§$', email="example2@mail.de")
        self.second_token = create_test_users_token(self.second_user)
        self.second_profile = create_test_users_profile(self.second_user, 'customer')
        self.min_price = 50
        self.min_delivery_time = 5
        self.updated_price = 40
        self.updated_delivery_time = 8
        self.new_min_price = self.updated_delivery_time
        self.new_min_delivery_time = 7

        # Default POST request payload for Offer creation
        self.post_request_body = {
            "title": "Grafikdesign-Paket",
            "image": None,
            "description": "Ein umfassendes Grafikdesign-Paket für Unternehmen.",
            "details": [
                {
                    "title": "Basic Design",
                    "revisions": 2,
                    "delivery_time_in_days": self.min_delivery_time,
                    "price": 50,
                    "features": [
                        "Logo Design",
                        "Visitenkarte"
                    ],
                    "offer_type": "basic"
                },
                {
                    "title": "Standard Design",
                    "revisions": 5,
                    "delivery_time_in_days": self.new_min_delivery_time,
                    "price": self.min_price,
                    "features": [
                        "Logo Design",
                        "Visitenkarte",
                        "Briefpapier"
                    ],
                    "offer_type": "standard"
                },
                {
                    "title": "Premium Design",
                    "revisions": 10,
                    "delivery_time_in_days": 10,
                    "price": 500,
                    "features": [
                        "Logo Design",
                        "Visitenkarte",
                        "Briefpapier",
                        "Flyer"
                    ],
                    "offer_type": "premium"
                }
            ]
        }

        # Create one default Offer for use in tests
        self.offer = Offer.objects.create(user=self.user, created_at=timezone.now(), title=self.post_request_body['title'], description=self.post_request_body['description'])
        self.url_detail = reverse('offers-detail', kwargs={'pk': self.offer.pk})
        self.url_list = reverse('offers-list')
        
        # Independent Detail object for dedicated detail tests
        self.detail = Detail.objects.create(
            title="Basic Design",
            revisions=10,
            delivery_time_in_days=self.min_delivery_time,
            price=self.min_price,
            features=[
                        "Logo Design",
                        "Visitenkarte",
                        "Briefpapier",
                        "Flyer"
                ],
            offer_type='basic',
            offer_id=self.offer.pk
        )
        Detail.objects.create(
            title="Basic Design",
            revisions=10,
            delivery_time_in_days=15,
            price=999,
            features=[
                        "Logo Design",
                        "Visitenkarte",
                        "Briefpapier",
                        "Flyer"
                ],
            offer_type='premium',
            offer_id=self.offer.pk
        )
        Detail.objects.create(
            title="Basic Design",
            revisions=10,
            delivery_time_in_days=15,
            price=999,
            features=[
                        "Logo Design",
                        "Visitenkarte",
                        "Briefpapier",
                        "Flyer"
                ],
            offer_type='standard',
            offer_id=self.offer.pk
        )

        # Request body for partial updates (PATCH)
        self.patch_request_body = {
            "title": "Updated Grafikdesign-Paket",
            "details": [
                {
                    "title": "Basic Design Updated",
                    "revisions": 3,
                    "delivery_time_in_days": self.updated_delivery_time,
                    "price": self.updated_price,
                    "features": [
                        "Logo Design",
                        "Flyer"
                    ],
                    "offer_type": "basic"
                }
            ]
        }


    def test_get_detail_success(self):
        """
        Ensure a single Offer can be retrieved successfully
        with all expected fields and correct values.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        expected_fields = {
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time"
        }
        response = self.client.get(self.url_detail)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), expected_fields)
        self.assertIsInstance(response.data["id"], int)
        self.assertIsInstance(response.data["user"], int)
        self.assertIsInstance(response.data["title"], str)
        self.assertIsInstance(response.data["description"], str)
        self.assertIsInstance(response.data["details"], list)
        self.assertIsInstance(response.data["min_price"], int)
        self.assertIsInstance(response.data["min_delivery_time"], int)
        self.assertEqual(len(response.data["details"]), 3)
        self.assertEqual(response.data["min_price"], self.min_price)
        self.assertEqual(response.data["min_delivery_time"], self.min_delivery_time)


    def test_get_detail_fails(self):
        """
        Ensure unauthorized access or invalid primary key
        returns proper error codes.
        """
        cases = [
            (None, self.url_detail, status.HTTP_401_UNAUTHORIZED), 
            (self.token.key, reverse('offers-detail', kwargs={'pk': 9999}), status.HTTP_404_NOT_FOUND)
        ]
        for token, url, expected in cases:
            if token:
                self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
            response = self.client.get(url)
            self.assertEqual(response.status_code, expected)


    def test_patch_detail_succsess(self):
        """
        Ensure an Offer can be partially updated successfully.
        Validates fields, details, and recalculated min values.
        """
        expected_fields_detail = {
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type"
        }
        request_detail = self.patch_request_body['details'][0]
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        response = self.client.patch(self.url_detail, self.patch_request_body, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for detail in response.data['details']:
            self.assertTrue(Detail.objects.filter(id=detail['id']).exists())
            self.assertEqual(set(detail.keys()), expected_fields_detail)
        for detail in response.data['details']:
            if detail['offer_type'] == 'basic':
                basic_detail = detail
        self.assertEqual(response.data['title'], self.patch_request_body['title'])
        self.assertEqual(basic_detail['title'], request_detail['title'])
        self.assertEqual(basic_detail['delivery_time_in_days'], request_detail['delivery_time_in_days'])
        self.assertEqual(set(basic_detail['features']), set(request_detail['features']))
        self.assertEqual(basic_detail['revisions'], request_detail['revisions'])
        self.assertEqual(basic_detail['price'], request_detail['price'])


    def test_patch_detail_fails(self):
        """
        Ensure patching an Offer fails with invalid data,
        unauthorized access, forbidden access, or invalid ID.
        """
        wrong_data = {
            "title": "Updated Grafikdesign-Paket",
            "details": [
                {
                    "title": "Basic Design Updated",
                    "revisions": 3,
                    "delivery_time_in_days": self.updated_delivery_time,
                    "price": self.updated_price,
                    "features": [
                        "Logo Design",
                        "Flyer"
                    ],
                    "offer_type": ""
                }
            ]
        }
        cases = [
            (self.url_detail, None, self.patch_request_body, status.HTTP_401_UNAUTHORIZED), 
            (self.url_detail, self.second_token.key, self.patch_request_body, status.HTTP_403_FORBIDDEN),
            (self.url_detail, self.token.key, wrong_data, status.HTTP_400_BAD_REQUEST),
            (reverse('offers-detail', kwargs={'pk': 9999}), self.token.key, self.patch_request_body, status.HTTP_404_NOT_FOUND)
        ]
        for url, token, data, expected in cases:
            if token:
                self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
            response = self.client.patch(url, data, format='json')
            self.assertEqual(response.status_code, expected)


    def test_delete_detail(self):
        """
        Ensure Offers can be deleted with proper authorization
        and correct error codes for invalid cases.
        """
        offer = self.create_offer(self.user)
        url = reverse('offers-detail', kwargs={'pk': offer.pk})
        cases = [
            (None, status.HTTP_401_UNAUTHORIZED),
            (self.second_token, status.HTTP_403_FORBIDDEN),
            (self.token, status.HTTP_204_NO_CONTENT),
            (self.token, status.HTTP_404_NOT_FOUND)
        ]
        for token, expected in cases:
            if token:
                self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
            response = self.client.delete(url)
            self.assertEqual(response.status_code, expected)


    def test_post_success(self):
        """
        Ensure an Offer can be created successfully.
        Validates fields, details, and persisted objects.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        expected_fields = {
            "id",
            "title",
            "image",
            "description",
            "details"
        }
        expected_fields_detail = {
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type"
        }
        response = self.client.post(self.url_list, self.post_request_body, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Offer.objects.filter(title=self.post_request_body['title']).exists())
        self.assertEqual(set(response.data.keys()), expected_fields)
        self.assertEqual(response.data['title'], self.post_request_body['title'])
        self.assertEqual(response.data['description'], self.post_request_body['description'])
        for detail in response.data['details']:
            self.assertTrue(Detail.objects.filter(id=detail['id']).exists())
            self.assertEqual(set(detail.keys()), expected_fields_detail)
        offer_types = {detail["offer_type"] for detail in response.data["details"]}
        self.assertSetEqual(offer_types, {"basic", "standard", "premium"})


    def test_post_fails(self):
        """
        Ensure Offer creation fails without token,
        with wrong permissions, or invalid detail data.
        """
        wrong_data = copy.deepcopy(self.post_request_body)
        wrong_data['details'] = [self.post_request_body['details'][1]]
        cases = [
            (None, self.post_request_body, status.HTTP_401_UNAUTHORIZED), 
            (self.second_token.key, self.post_request_body, status.HTTP_403_FORBIDDEN),
            (self.token.key, wrong_data, status.HTTP_400_BAD_REQUEST)
        ]
        for token, data, expected in cases:
            if token:
                self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
            response = self.client.post(self.url_list, data, format='json')
            self.assertEqual(response.status_code, expected)


    def test_get_list_success(self):
        """
        Ensure Offers list endpoint works with filtering,
        ordering, searching, pagination, and correct structure.
        """
        expected_response_fields = {
            'count',
            'next',
            'previous',
            'results'
        }
        expected_results_fields = {
            'id',
            'user',
            'title',
            'image',
            'description',
            'created_at',
            'updated_at',
            'details',
            'min_price',
            'min_delivery_time',
            'user_details'
        }
        expected_detail_fields = {
            'id',
            'url'
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        param_tests = [
            ({'creator_id': self.user.id}, lambda offers: all(offer['user'] == self.user.id for offer in offers)),
            ({'min_price': self.min_price}, lambda offers: all(offer['min_price'] >= self.min_price for offer in offers)),
            ({'max_delivery_time': self.min_delivery_time}, lambda offers: all(offer['min_delivery_time'] <= self.min_delivery_time for offer in offers)),
            ({'ordering': 'min_price'}, lambda offers: [offer['min_price'] for offer in offers] == sorted([offer['min_price'] for offer in offers])),
            ({'ordering': 'created_at'}, lambda offers: [offer['created_at'] for offer in offers] == sorted([offer['created_at'] for offer in offers], reverse=True)),
            ({'search': 'Grafikdesign'}, lambda offers: all('Grafikdesign' in offer['title'] or 'grafikdesign' in offer['description'] for offer in offers)),
            ({'page_size': 2}, lambda offers: len(offers) <= 2 and len(offers) >= 1)
        ]
        
        response = self.client.get(self.url_list)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data['results'], list)
        for offer in response.data['results']:
            self.assertTrue(Offer.objects.filter(id=offer['id']).exists())
            self.assertEqual(set(offer.keys()), expected_results_fields)
            for detail in offer['details']:
                self.assertTrue(Detail.objects.filter(id=detail['id']).exists())
                self.assertEqual(set(detail.keys()), expected_detail_fields)
        for params, check in param_tests:
            response = self.client.get(self.url_list, params)
            offers = response.data.get('results', response.data)
            self.assertGreaterEqual(len(offers), 1, f"Param test returned no offers for params: {params}")
            self.assertTrue(check(offers))
        self.assertEqual(set(response.data.keys()), expected_response_fields)

        # Check content of a specific Offer returned in the list
        api_offer = next(filter(lambda offer: offer['id'] == self.offer.pk, offers), None)
        self.assertEqual(api_offer['title'], self.offer.title)
        self.assertEqual(api_offer['description'], self.offer.description)
        self.assertEqual(api_offer['min_price'], self.min_price)
        self.assertEqual(api_offer['min_delivery_time'], self.min_delivery_time)
        self.assertGreaterEqual(len(api_offer['details']), 3)

        # Verify correct detail fields inside the offer
        basic_detail = next(Detail.objects.get(id=detail['id']) for detail in api_offer['details'] if Detail.objects.get(id=detail['id']).offer_type == 'basic')
        self.assertEqual(basic_detail.price, self.min_price)
        self.assertEqual(basic_detail.delivery_time_in_days, self.min_delivery_time)


    def test_get_detail_offers_detail_success(self):
        """
        Ensure a single Detail object can be retrieved successfully
        with all expected fields and values.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        expected_fields = {
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type"
        }

        response = self.client.get(reverse('detail-detail', kwargs={'pk': self.detail.pk}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), expected_fields)
        self.assertEqual(response.data['title'], self.detail.title)
        self.assertEqual(response.data['revisions'], self.detail.revisions)
        self.assertEqual(response.data['offer_type'], self.detail.offer_type)
        self.assertIsInstance(response.data['features'], list)


    def test_get_detail_offers_detail_fails(self):
        """
        Ensure unauthorized access or invalid primary key for Detail view
        returns correct error codes.
        """
        response = self.client.get(reverse('detail-detail', kwargs={'pk': self.detail.pk}))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        response = self.client.get(reverse('detail-detail', kwargs={'pk': 9999}))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
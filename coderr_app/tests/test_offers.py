import copy
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from auth_app.tests.test_auth import create_test_image_file, create_test_user, create_test_users_token, create_test_users_profile
from coderr_app.models import Offer, Detail

class OffersTests(APITestCase):
    def create_offer(self, user):
            return Offer.objects.create(
            user=user,
            title='Testtitle',
            image=create_test_image_file(),
            description="Test",
            details=[self.post_request_body['details'][0], self.post_request_body['details'][1], self.post_request_body['details'][2]]
        )


    def setUp(self):
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
        self.post_request_body = {
            "title": "Grafikdesign-Paket",
            "image": create_test_image_file(),
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
        
        self.offer = self.create_offer(user=self.user)
        self.url_detail = reverse('offers-detail', kwargs={'pk': self.offer.pk})
        self.url_list = reverse('offers-list')

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


    def test_get_detail_sccess(self):
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
        self.assertGreaterEqual(len(response.data["details"]), 3)
        self.assertEqual(response.data["min_price"], self.min_price)
        self.assertEqual(response.data["min_delivery_time"], self.min_delivery_time)


    def test_get_detail_fails(self):
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
        count_offer_type = 0

        response = self.client.patch(self.url_detail, self.patch_request_body, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for detail in response.data['details']:
            self.assertTrue(Detail.objects.filter(id=detail['id']).exists())
            self.assertEqual(set(detail.keys()), expected_fields_detail)
            if detail['offer_type'] == 'basic':
                basic_detail = detail
                count_offer_type += 1
        self.assertEqual(count_offer_type, 1)
        self.assertEqual(response.data['title'], self.patch_request_body['title'])
        self.assertEqual(basic_detail['title'], request_detail['title'])
        self.assertEqual(basic_detail['delivery_time_in_days'], request_detail['delivery_time_in_days'])
        self.assertEqual(response.data["min_price"], self.new_min_price)
        self.assertEqual(response.data["min_delivery_time"], self.new_min_delivery_time)
        self.assertEqual(set(basic_detail['features']), set(request_detail['features']))
        self.assertEqual(basic_detail['revisions'], request_detail['revisions'])
        self.assertEqual(basic_detail['price'], request_detail['price'])


    def test_patch_detail_fails(self):
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
            response = self.client.patch(url, data, format='multipart')
            self.assertEqual(response.status_code, expected)


    def test_delete_detail(self):
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
                self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
            response = self.client.delete(url)
            self.assertEqual(response.status_code, expected)


    def test_post_success(self):
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

        response = self.client.post(self.url_list, self.post_request_body, format='multipart')

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
            response = self.client.post(self.url_list, data, format='multipart')
            self.assertEqual(response.status_code, expected)
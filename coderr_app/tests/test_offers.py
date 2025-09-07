from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from PIL import Image
from io import BytesIO
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from auth_app.tests.test_auth import create_test_image_file, create_test_users_profile, create_test_users_token, create_test_user

class OffersTests(APITestCase):
    
    def setUp(self):
        self.post_request_body = {
            "title": "Grafikdesign-Paket",
            "image": create_test_image_file(),
            "description": "Ein umfassendes Grafikdesign-Paket für Unternehmen.",
            "details": [
                {
                    "title": "Basic Design",
                    "revisions": 2,
                    "delivery_time_in_days": 5,
                    "price": 100,
                    "features": [
                        "Logo Design",
                        "Visitenkarte"
                    ],
                    "offer_type": "basic"
                },
                {
                    "title": "Standard Design",
                    "revisions": 5,
                    "delivery_time_in_days": 7,
                    "price": 200,
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

        self.post_request_body = {
            "title": "Updated Grafikdesign-Paket",
            "details": [
                {
                    "title": "Basic Design Updated",
                    "revisions": 3,
                    "delivery_time_in_days": 6,
                    "price": 120,
                    "features": [
                        "Logo Design",
                        "Flyer"
                    ],
                    "offer_type": "basic"
                }
            ]
        }

        self.user = create_test_user()
        self.token = create_test_users_token(self.user)
        self.profile = create_test_users_profile(self.user)
        self.url_detail = reverse('offers-detail', kwargs={'pk': self.offer.pk})
        self.second_user = create_test_user(username='Test2', password='Test12§$')
        self.second_token = create_test_users_token(self.second_user)
        self.second_profile = create_test_users_profile(self.second_user, 'customer')



    
    def test_get_detail_sccess(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        response = self.client.get(self.url_detail)
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
from coderr_app.models import Review
from .utils import create_offer, create_detail_set

class ReviewsTests(APITestCase):
    def setUp(self):
        self.expected_fields = [
            'id',
            'business_user',
            'rewiewer',
            'rating',
            'description',
            'created_at',
            'updated_at'
        ]
        self.user_business = create_test_user()
        self.token_business = create_test_users_token(self.user_business)
        self.profile_business = create_test_users_profile(self.user_business)
        self.user_business_2 = create_test_user()
        self.token_business_2 = create_test_users_token(self.user_business_2)
        self.profile_business_2 = create_test_users_profile(self.user_business_2)
        self.user_customer = create_test_user(username='customer')
        self.token_customer = create_test_users_token(self.user_customer)
        self.profile_customer = create_test_users_profile(self.user_customer, 'customer')
        self.review = Review.objects.create(
            business_user=self.user_business,
            reviewer=self.user_customer,
            rating=4,
            description='Test!',
            created_at=timezone.now()
        )
        self.url_list = reverse('reviews-list')
        self.url_detail = reverse('reviews-detail', kwargs={'pk': self.review.pk})
        self.post_request_body = {
            "business_user": self.user_business_2,
            "rating": 2,
            "description": "Post test!"
        }
        

    def tearDown(self):
        delete_test_images()
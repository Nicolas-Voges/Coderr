from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from PIL import Image
from io import BytesIO
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

class OffersTests(APITestCase):
    pass
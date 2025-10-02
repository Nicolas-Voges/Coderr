import os
from PIL import Image
from io import BytesIO
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from auth_app.models import Profile

FOLDERS_TO_CLEAN = ['user_images', 'offer_images']

username = "exampleUsername"
password = "examplePassword"
email = "example@mail.de"
first_name = 'Max'
last_name = ''
image_name = "test_image.jpg"

def create_test_image_file():
    """Create and return a small test image file."""
    image = BytesIO()
    img = Image.new('RGB', (10, 10), color='red')
    img.save(image, format='JPEG')
    image.seek(0)
    return SimpleUploadedFile(image_name, image.read(), content_type='image/jpeg')


def create_test_user(
        username = username,
        password = password,
        email = email,
        first_name = first_name,
        last_name = last_name,
):
    return User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name
        )


def create_test_users_token(user):
    return Token.objects.create(user=user)


def create_test_users_profile(user, type='business'):
    return Profile.objects.create(
            user=user,
            file=create_test_image_file(),
            location="Berlin",
            tel="+49531697151",
            description="Business description",
            working_hours="9-17",
            type=type,
            created_at=timezone.now()
        )


def delete_test_images():
    """
    Delete all test images in media/user_images/ and media/Offer_images/
    that start with 'test_image'.
    """
    for folder in FOLDERS_TO_CLEAN:
        folder_path = os.path.join(settings.MEDIA_ROOT, folder)
        if not os.path.exists(folder_path):
            continue

        for root, dirs, files in os.walk(folder_path):
            for filename in files:
                if filename.startswith("test_image"):
                    file_path = os.path.join(root, filename)
                    try:
                        os.remove(file_path)
                    except Exception as error:
                        print(f"Could not delete {file_path}: {error}")
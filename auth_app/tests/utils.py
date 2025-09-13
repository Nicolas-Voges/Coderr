from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from auth_app.models import Profile

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
from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.

class UserType(models.TextChoices):
    customer = 'customer', 'Customer'
    business = 'business', 'Business'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    file = models.ImageField(upload_to='user_images/')
    location = models.CharField(max_length=30)
    tel = PhoneNumberField()
    description = models.CharField(max_length=255)
    working_hours = models.CharField(max_length=20)
    type = models.CharField(max_length=20, choices=UserType.choices, default=UserType.customer)
    email = models.EmailField()
    created_at = models.DateTimeField()
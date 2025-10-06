"""
Django models for user profiles.

This module extends the built-in User model with additional
profile information such as image, phone number, and user type.
"""

from phonenumber_field.modelfields import PhoneNumberField

from django.db import models
from django.contrib.auth.models import User

class UserType(models.TextChoices):
    """Enumeration of possible user types."""
    customer = 'customer', 'Customer'
    business = 'business', 'Business'

class Profile(models.Model):
    """
    Extended profile information for a Django User.

    Stores additional user-related data such as profile picture,
    contact details, account type, and timestamps.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    file = models.ImageField(upload_to='user_images/')
    location = models.CharField(max_length=30)
    tel = PhoneNumberField()
    description = models.CharField(max_length=255)
    working_hours = models.CharField(max_length=20)
    type = models.CharField(max_length=20, choices=UserType.choices, default=UserType.customer)
    created_at = models.DateTimeField()
    uploaded_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        """Return a string representation of the profile with user ID."""
        return f"Profile {self.id} from user {self.user.id}"
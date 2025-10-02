from django.db import models
from django.contrib.auth.models import User

class DetailType(models.TextChoices):
    basic = 'basic', "Basic"
    standard = 'standard', "Standard"
    premium = 'premium', "Premium"


class Offer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offer')
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to='offer_images/', blank=True, null=True)
    description = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)


class Detail(models.Model):
    title = models.CharField(max_length=50)
    revisions = models.IntegerField()
    delivery_time_in_days = models.IntegerField()
    price = models.FloatField()
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=20, choices=DetailType.choices, default=DetailType.basic)
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='details')


class StatusType(models.TextChoices):
    in_progress = 'in_progress', 'In Progress'
    completed = 'completed', "Completed"
    cancelled = 'cancelled', "Cancelled"

class Order(models.Model):
    customer_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_order')
    business_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='business_order')
    status = models.CharField(max_length=20, choices=StatusType.choices, default=StatusType.in_progress)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)
    offer_detail = models.ForeignKey(Detail, on_delete=models.CASCADE, related_name='order')
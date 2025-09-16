from django.db import models
from django.contrib.auth.models import User

class DetailType(models.TextChoices):
    basic = 'basic', 'Basic'
    standard = 'standard', 'Standard'
    premium = 'premium', 'Premium'


class Offer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to='user_images/')
    description = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    min_price = models.IntegerField()
    min_delivery_time = models.IntegerField()


class Detail(models.Model):
    title = models.CharField(max_length=50)
    revisions = models.IntegerField()
    delivery_time_in_days = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=20, choices=DetailType.choices, default=DetailType.basic)
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='details')
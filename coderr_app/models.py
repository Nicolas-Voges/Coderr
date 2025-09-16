from django.db import models

class DetailType(models.TextChoices):
    basic = 'basic', 'Basic'
    standard = 'standard', 'Standard'
    premium = 'premium', 'Premium'

    
class Detail(models.Model):
    title = models.CharField(max_length=50)
    revisions = models.IntegerField()
    delivery_time_in_days = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=20, choices=DetailType.choices, default=DetailType.basic)
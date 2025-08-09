# Create your models here.
from django.db import models
from accounts.models import User

class WaterType(models.Model):
    WATER_TYPES = (
        ('dispenser', 'Dispenser'),
        ('bottle', 'Bottle'),
    )
    
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'vendor'})
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=WATER_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    size = models.CharField(max_length=50)  # e.g., "20L", "500ml"
    description = models.TextField(blank=True)
# Create your models here.
from django.db import models
from accounts.models import User
from products.models import WaterType

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    water_type = models.ForeignKey(WaterType, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    delivery_latitude = models.FloatField()  # Store delivery location latitude
    delivery_longitude = models.FloatField()  # Store delivery location longitude
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rider = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'user_type': 'rider'})
    created_at = models.DateTimeField(auto_now_add=True)
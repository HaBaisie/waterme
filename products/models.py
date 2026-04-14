from django.conf import settings
from django.db import models


class VendorProfile(models.Model):
    VERIFICATION_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vendor_profile')
    business_name = models.CharField(max_length=150)
    avatar_url = models.URLField(blank=True)
    service_area_latitude = models.FloatField()
    service_area_longitude = models.FloatField()
    service_radius_km = models.DecimalField(max_digits=6, decimal_places=2, default=10)
    price_per_litre = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_litres = models.PositiveIntegerField(default=500)
    max_order_litres = models.PositiveIntegerField(default=10000)
    tanker_capacity_litres = models.PositiveIntegerField(default=10000)
    available_litres = models.PositiveIntegerField(default=0)
    available = models.BooleanField(default=False)
    eta_minutes = models.PositiveIntegerField(default=30)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS_CHOICES, default='pending')
    bank_code = models.CharField(max_length=20, blank=True)
    account_number = models.CharField(max_length=20, blank=True)
    account_name = models.CharField(max_length=100, blank=True)
    schedule = models.JSONField(default=dict, blank=True)
    rating_average = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    review_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['business_name']

    def __str__(self):
        return self.business_name


class WaterType(models.Model):
    WATER_TYPES = (
        ('dispenser', 'Dispenser'),
        ('bottle', 'Bottle'),
    )

    vendor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'user_type': 'vendor'})
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=WATER_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    size = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    def __str__(self):
        return f'{self.name} ({self.size})'
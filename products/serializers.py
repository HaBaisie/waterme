from rest_framework import serializers
from .models import WaterType
from accounts.serializers import UserSerializer

class WaterTypeSerializer(serializers.ModelSerializer):
    vendor = UserSerializer(read_only=True)
    
    class Meta:
        model = WaterType
        fields = ['id', 'vendor', 'name', 'type', 'price', 'size', 'description']
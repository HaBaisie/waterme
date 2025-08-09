from rest_framework import serializers
from .models import Order
from products.models import WaterType  # Add this import
from products.serializers import WaterTypeSerializer
from accounts.serializers import UserSerializer
from geopy.distance import geodesic

class OrderSerializer(serializers.ModelSerializer):
    water_type = WaterTypeSerializer(read_only=True)
    water_type_id = serializers.PrimaryKeyRelatedField(
        queryset=WaterType.objects.all(), source='water_type', write_only=True)
    user = UserSerializer(read_only=True)
    rider = UserSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'water_type', 'water_type_id', 'quantity', 'delivery_latitude',
                  'delivery_longitude', 'delivery_fee', 'total_amount', 'status', 'rider', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user
        water_type = validated_data['water_type']
        quantity = validated_data['quantity']
        
        # Calculate delivery fee based on distance
        vendor_location = (water_type.vendor.latitude, water_type.vendor.longitude)
        delivery_location = (validated_data['delivery_latitude'], validated_data['delivery_longitude'])
        
        if None in vendor_location or None in delivery_location:
            raise serializers.ValidationError("Invalid location data")
        
        distance = geodesic(vendor_location, delivery_location).km
        delivery_fee = distance * 2.0  # Example: $2 per km
        
        total_amount = (water_type.price * quantity) + delivery_fee
        
        order = Order.objects.create(
            user=user,
            water_type=water_type,
            quantity=quantity,
            delivery_latitude=validated_data['delivery_latitude'],
            delivery_longitude=validated_data['delivery_longitude'],
            delivery_fee=delivery_fee,
            total_amount=total_amount
        )
        return order

class OrderSerializer(serializers.ModelSerializer):
    water_type = WaterTypeSerializer(read_only=True)
    water_type_id = serializers.PrimaryKeyRelatedField(
        queryset=WaterType.objects.all(), source='water_type', write_only=True)
    user = UserSerializer(read_only=True)
    rider = UserSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'water_type', 'water_type_id', 'quantity', 'delivery_latitude',
                  'delivery_longitude', 'delivery_fee', 'total_amount', 'status', 'rider', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user
        water_type = validated_data['water_type']
        quantity = validated_data['quantity']
        
        # Calculate delivery fee based on distance
        vendor_location = (water_type.vendor.latitude, water_type.vendor.longitude)
        delivery_location = (validated_data['delivery_latitude'], validated_data['delivery_longitude'])
        
        if None in vendor_location or None in delivery_location:
            raise serializers.ValidationError("Invalid location data")
        
        distance = geodesic(vendor_location, delivery_location).km
        delivery_fee = distance * 2.0  # Example: $2 per km
        
        total_amount = (water_type.price * quantity) + delivery_fee
        
        order = Order.objects.create(
            user=user,
            water_type=water_type,
            quantity=quantity,
            delivery_latitude=validated_data['delivery_latitude'],
            delivery_longitude=validated_data['delivery_longitude'],
            delivery_fee=delivery_fee,
            total_amount=total_amount
        )
        return order
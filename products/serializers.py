from rest_framework import serializers

from .models import VendorProfile, WaterType


class VendorProfileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user.id', read_only=True)
    phone_number = serializers.CharField(source='user.phone_number', read_only=True)
    distance_km = serializers.SerializerMethodField()

    class Meta:
        model = VendorProfile
        fields = [
            'id',
            'business_name',
            'avatar_url',
            'phone_number',
            'price_per_litre',
            'min_order_litres',
            'max_order_litres',
            'tanker_capacity_litres',
            'available_litres',
            'available',
            'eta_minutes',
            'service_area_latitude',
            'service_area_longitude',
            'service_radius_km',
            'verification_status',
            'schedule',
            'rating_average',
            'review_count',
            'distance_km',
        ]
        read_only_fields = ['id', 'verification_status', 'rating_average', 'review_count', 'distance_km']

    def get_distance_km(self, obj):
        return getattr(obj, 'distance_km', None)


class VendorRegistrationSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(write_only=True)
    service_area = serializers.DictField(write_only=True)
    bank_account = serializers.DictField(write_only=True, required=False)

    class Meta:
        model = VendorProfile
        fields = [
            'business_name',
            'avatar_url',
            'phone_number',
            'service_area',
            'price_per_litre',
            'min_order_litres',
            'max_order_litres',
            'tanker_capacity_litres',
            'available_litres',
            'eta_minutes',
            'bank_account',
        ]

    def validate_service_area(self, value):
        required_keys = {'lat', 'lng', 'radius_km'}
        if not required_keys.issubset(value.keys()):
            raise serializers.ValidationError('service_area must include lat, lng, and radius_km.')
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        phone_number = validated_data.pop('phone_number')
        service_area = validated_data.pop('service_area')
        bank_account = validated_data.pop('bank_account', {})

        user.user_type = 'vendor'
        user.phone_number = phone_number
        user.latitude = service_area['lat']
        user.longitude = service_area['lng']
        user.save(update_fields=['user_type', 'phone_number', 'latitude', 'longitude'])

        profile, _ = VendorProfile.objects.update_or_create(
            user=user,
            defaults={
                'business_name': validated_data['business_name'],
                'avatar_url': validated_data.get('avatar_url', ''),
                'service_area_latitude': service_area['lat'],
                'service_area_longitude': service_area['lng'],
                'service_radius_km': service_area['radius_km'],
                'price_per_litre': validated_data['price_per_litre'],
                'min_order_litres': validated_data.get('min_order_litres', 500),
                'max_order_litres': validated_data.get('max_order_litres', 10000),
                'tanker_capacity_litres': validated_data.get('tanker_capacity_litres', 10000),
                'available_litres': validated_data.get('available_litres', 0),
                'eta_minutes': validated_data.get('eta_minutes', 30),
                'bank_code': bank_account.get('bank_code', ''),
                'account_number': bank_account.get('account_number', ''),
                'account_name': bank_account.get('account_name', ''),
            },
        )
        return profile


class VendorAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorProfile
        fields = ['available', 'available_litres']


class VendorScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorProfile
        fields = ['schedule']


class WaterTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterType
        fields = ['id', 'name', 'type', 'price', 'size', 'description']
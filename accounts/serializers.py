from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import Address, User


def split_name(value):
    parts = value.strip().split(None, 1)
    first_name = parts[0] if parts else ''
    last_name = parts[1] if len(parts) > 1 else ''
    return first_name, last_name


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'label', 'full_address', 'latitude', 'longitude', 'is_default', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate(self, attrs):
        user = self.context['request'].user
        if self.instance is None and user.addresses.count() >= 5:
            raise serializers.ValidationError({'addresses': 'You can only save up to 5 addresses.'})
        return attrs

    def create(self, validated_data):
        return Address.objects.create(user=self.context['request'].user, **validated_data)


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    addresses = AddressSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'name',
            'email',
            'user_type',
            'phone_number',
            'address',
            'latitude',
            'longitude',
            'wallet_balance',
            'addresses',
        ]
        read_only_fields = ['id', 'wallet_balance', 'addresses']

    def get_name(self, obj):
        return obj.get_full_name() or obj.username


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'name', 'email', 'password', 'user_type', 'phone_number', 'address', 'latitude', 'longitude']

    def create(self, validated_data):
        name = validated_data.pop('name', '')
        first_name, last_name = split_name(name)
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            user_type=validated_data.get('user_type', 'regular'),
            phone_number=validated_data.get('phone_number', ''),
            address=validated_data.get('address', ''),
            latitude=validated_data.get('latitude'),
            longitude=validated_data.get('longitude'),
            first_name=first_name,
            last_name=last_name,
        )


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs.get('username'), password=attrs.get('password'))
        if user is None:
            raise serializers.ValidationError({'detail': 'Invalid credentials.'})
        attrs['user'] = user
        return attrs


class ProfileUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['name', 'email', 'phone_number', 'address', 'latitude', 'longitude']

    def update(self, instance, validated_data):
        name = validated_data.pop('name', None)
        if name is not None:
            instance.first_name, instance.last_name = split_name(name)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance
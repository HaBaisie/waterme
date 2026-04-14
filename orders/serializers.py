from decimal import Decimal

from django.db.models import Avg, Count
from django.utils import timezone
from geopy.distance import geodesic
from rest_framework import serializers

from accounts.models import Address, User
from accounts.serializers import AddressSerializer
from products.models import VendorProfile
from products.serializers import VendorProfileSerializer

from .models import Dispute, Order, Review


VALID_STATUS_TRANSITIONS = {
    'pending': {'accepted', 'cancelled'},
    'accepted': {'en_route', 'cancelled'},
    'en_route': {'delivered', 'cancelled'},
    'delivered': set(),
    'confirmed': set(),
    'cancelled': set(),
}


def update_vendor_rating(vendor):
    aggregates = Review.objects.filter(vendor=vendor).aggregate(avg=Avg('rating'), count=Count('id'))
    profile = vendor.vendor_profile
    profile.rating_average = aggregates['avg'] or 0
    profile.review_count = aggregates['count'] or 0
    profile.save(update_fields=['rating_average', 'review_count'])


class OrderReadSerializer(serializers.ModelSerializer):
    vendor = serializers.SerializerMethodField()
    delivery_address = AddressSerializer(read_only=True)
    quantity_litres = serializers.IntegerField(source='quantity', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'status',
            'vendor',
            'quantity_litres',
            'delivery_address',
            'scheduled_at',
            'payment_method',
            'payment_reference',
            'special_instructions',
            'unit_price',
            'delivery_fee',
            'total_amount',
            'eta_minutes',
            'cancellation_reason',
            'created_at',
            'updated_at',
        ]

    def get_vendor(self, obj):
        if obj.vendor_id and hasattr(obj.vendor, 'vendor_profile'):
            return VendorProfileSerializer(obj.vendor.vendor_profile).data
        return None


class OrderCreateSerializer(serializers.Serializer):
    vendor_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(user_type='vendor'), source='vendor')
    quantity_litres = serializers.IntegerField(min_value=1, source='quantity')
    delivery_address_id = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all(), source='delivery_address')
    scheduled_at = serializers.DateTimeField(required=False, allow_null=True)
    payment_method = serializers.ChoiceField(choices=Order.PAYMENT_METHOD_CHOICES)
    payment_reference = serializers.CharField(required=False, allow_blank=True)
    special_instructions = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        request = self.context['request']
        vendor = attrs['vendor']
        address = attrs['delivery_address']
        quantity = attrs['quantity']

        if request.user.user_type != 'regular':
            raise serializers.ValidationError({'detail': 'Only regular users can place orders.'})
        if address.user_id != request.user.id:
            raise serializers.ValidationError({'delivery_address_id': 'Address must belong to the current user.'})

        profile = getattr(vendor, 'vendor_profile', None)
        if profile is None or profile.verification_status != 'approved':
            raise serializers.ValidationError({'vendor_id': 'Vendor is not available for ordering.'})
        if not profile.available:
            raise serializers.ValidationError({'vendor_id': 'Vendor is currently offline.'})
        if quantity < profile.min_order_litres or quantity > profile.max_order_litres:
            raise serializers.ValidationError({'quantity_litres': 'Quantity is outside the vendor order limits.'})
        if quantity > profile.available_litres:
            raise serializers.ValidationError({'quantity_litres': 'Vendor does not have enough available litres.'})

        distance_km = Decimal(
            str(
                geodesic(
                    (profile.service_area_latitude, profile.service_area_longitude),
                    (address.latitude, address.longitude),
                ).km
            )
        ).quantize(Decimal('0.01'))
        if distance_km > profile.service_radius_km:
            raise serializers.ValidationError({'vendor_id': 'Delivery address is outside the vendor service area.'})

        attrs['vendor_profile'] = profile
        attrs['distance_km'] = distance_km
        return attrs

    def create(self, validated_data):
        request = self.context['request']
        address = validated_data['delivery_address']
        vendor_profile = validated_data.pop('vendor_profile')
        distance_km = validated_data.pop('distance_km')
        quantity = validated_data['quantity']

        unit_price = vendor_profile.price_per_litre
        delivery_fee = max(Decimal('500.00'), (distance_km * Decimal('100.00')).quantize(Decimal('0.01')))
        total_amount = (unit_price * Decimal(quantity)).quantize(Decimal('0.01')) + delivery_fee
        eta_minutes = vendor_profile.eta_minutes + int(distance_km)

        order = Order.objects.create(
            user=request.user,
            vendor=validated_data['vendor'],
            delivery_address=address,
            quantity=quantity,
            delivery_latitude=address.latitude,
            delivery_longitude=address.longitude,
            unit_price=unit_price,
            delivery_fee=delivery_fee,
            total_amount=total_amount,
            eta_minutes=eta_minutes,
            scheduled_at=validated_data.get('scheduled_at'),
            payment_method=validated_data['payment_method'],
            payment_reference=validated_data.get('payment_reference', ''),
            special_instructions=validated_data.get('special_instructions', ''),
        )

        vendor_profile.available_litres -= quantity
        vendor_profile.available = vendor_profile.available_litres > 0
        vendor_profile.save(update_fields=['available_litres', 'available'])
        return order


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['accepted', 'en_route', 'delivered', 'cancelled'])
    cancellation_reason = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        order = self.context['order']
        next_status = attrs['status']
        if next_status not in VALID_STATUS_TRANSITIONS.get(order.status, set()):
            raise serializers.ValidationError({'status': 'The requested status transition is not allowed.'})
        if next_status == 'cancelled' and not attrs.get('cancellation_reason'):
            raise serializers.ValidationError({'cancellation_reason': 'Cancellation reason is required.'})
        return attrs

    def save(self, **kwargs):
        order = self.context['order']
        next_status = self.validated_data['status']
        order.status = next_status
        if next_status == 'accepted':
            order.accepted_at = timezone.now()
        elif next_status == 'delivered':
            order.delivered_at = timezone.now()
        elif next_status == 'cancelled':
            order.cancellation_reason = self.validated_data['cancellation_reason']
            if order.vendor_id and hasattr(order.vendor, 'vendor_profile'):
                profile = order.vendor.vendor_profile
                profile.available_litres += order.quantity
                profile.available = True
                profile.save(update_fields=['available_litres', 'available'])
        order.save()
        return order


class OrderCancelSerializer(serializers.Serializer):
    reason = serializers.CharField()


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['rating', 'comment']

    def validate(self, attrs):
        order = self.context['order']
        request = self.context['request']
        if order.user_id != request.user.id:
            raise serializers.ValidationError({'detail': 'You can only review your own orders.'})
        if order.status not in {'delivered', 'confirmed'}:
            raise serializers.ValidationError({'detail': 'You can only review a delivered order.'})
        if hasattr(order, 'review'):
            raise serializers.ValidationError({'detail': 'A review already exists for this order.'})
        return attrs

    def create(self, validated_data):
        order = self.context['order']
        review = Review.objects.create(order=order, user=order.user, vendor=order.vendor, **validated_data)
        update_vendor_rating(order.vendor)
        return review


class DisputeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dispute
        fields = ['reason', 'description', 'evidence_url']

    def validate(self, attrs):
        order = self.context['order']
        request = self.context['request']
        if order.user_id != request.user.id:
            raise serializers.ValidationError({'detail': 'You can only dispute your own orders.'})
        if order.disputes.filter(status__in=['open', 'under_review']).exists():
            raise serializers.ValidationError({'detail': 'A dispute is already open for this order.'})
        return attrs

    def create(self, validated_data):
        order = self.context['order']
        return Dispute.objects.create(order=order, user=order.user, **validated_data)
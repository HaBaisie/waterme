from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Address
from orders.models import Order, Review
from products.models import VendorProfile


User = get_user_model()


class OrderApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user1', password='strongpass123', user_type='regular')
        self.vendor = User.objects.create_user(username='vendor1', password='strongpass123', user_type='vendor')
        self.vendor_profile = VendorProfile.objects.create(
            user=self.vendor,
            business_name='Al-Amin Water Supply',
            service_area_latitude=8.4890,
            service_area_longitude=4.5310,
            service_radius_km='10.00',
            price_per_litre='12.50',
            min_order_litres=500,
            max_order_litres=10000,
            tanker_capacity_litres=10000,
            available_litres=8000,
            available=True,
            verification_status='approved',
        )
        self.address = Address.objects.create(
            user=self.user,
            label='Home',
            full_address='12 Unity Road, Ilorin',
            latitude=8.4966,
            longitude=4.5421,
            is_default=True,
        )

    def test_order_lifecycle_and_review(self):
        self.client.force_authenticate(user=self.user)
        create_response = self.client.post(
            '/api/orders/',
            {
                'vendor_id': self.vendor.id,
                'quantity_litres': 1000,
                'delivery_address_id': self.address.id,
                'payment_method': 'card',
                'payment_reference': 'pay_ref_abc123',
                'special_instructions': 'Blue gate, ring twice',
            },
            format='json',
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        order_id = create_response.data['id']

        self.client.force_authenticate(user=self.vendor)
        accepted_response = self.client.patch(
            f'/api/orders/{order_id}/status/',
            {'status': 'accepted'},
            format='json',
        )
        self.assertEqual(accepted_response.status_code, status.HTTP_200_OK)

        en_route_response = self.client.patch(
            f'/api/orders/{order_id}/status/',
            {'status': 'en_route'},
            format='json',
        )
        self.assertEqual(en_route_response.status_code, status.HTTP_200_OK)

        delivered_response = self.client.patch(
            f'/api/orders/{order_id}/status/',
            {'status': 'delivered'},
            format='json',
        )
        self.assertEqual(delivered_response.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=self.user)
        confirm_response = self.client.post(f'/api/orders/{order_id}/confirm-delivery/', format='json')
        self.assertEqual(confirm_response.status_code, status.HTTP_200_OK)

        review_response = self.client.post(
            f'/api/orders/{order_id}/review/',
            {'rating': 5, 'comment': 'Very fast delivery.'},
            format='json',
        )
        self.assertEqual(review_response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Review.objects.filter(order_id=order_id).exists())
        self.assertEqual(Order.objects.get(pk=order_id).status, 'confirmed')

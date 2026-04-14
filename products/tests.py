from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from products.models import VendorProfile


User = get_user_model()


class VendorApiTests(APITestCase):
    def test_vendor_registration_and_nearby_listing(self):
        vendor_user = User.objects.create_user(username='vendor1', password='strongpass123', user_type='regular')
        self.client.force_authenticate(user=vendor_user)
        registration_response = self.client.post(
            '/api/vendors/register/',
            {
                'business_name': 'Al-Amin Water Supply',
                'phone_number': '+2348023456789',
                'service_area': {'lat': 8.4890, 'lng': 4.5310, 'radius_km': 8},
                'price_per_litre': '12.50',
                'min_order_litres': 500,
                'max_order_litres': 10000,
                'tanker_capacity_litres': 10000,
                'available_litres': 8000,
                'bank_account': {
                    'bank_code': '057',
                    'account_number': '1234567890',
                    'account_name': 'Abdullahi Musa',
                },
            },
            format='json',
        )
        self.assertEqual(registration_response.status_code, status.HTTP_201_CREATED)

        profile = VendorProfile.objects.get(user=vendor_user)
        profile.verification_status = 'approved'
        profile.available = True
        profile.save(update_fields=['verification_status', 'available'])

        self.client.force_authenticate(user=vendor_user)
        availability_response = self.client.patch(
            '/api/vendors/me/availability/',
            {'available': True, 'available_litres': 7000},
            format='json',
        )
        self.assertEqual(availability_response.status_code, status.HTTP_200_OK)

        buyer = User.objects.create_user(username='buyer1', password='strongpass123', user_type='regular')
        self.client.force_authenticate(user=buyer)
        list_response = self.client.get('/api/vendors/')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data['total'], 1)
        self.assertEqual(list_response.data['vendors'][0]['business_name'], 'Al-Amin Water Supply')

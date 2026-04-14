from rest_framework import status
from rest_framework.test import APITestCase


class AuthProfileApiTests(APITestCase):
    def test_register_login_profile_and_address_flow(self):
        register_response = self.client.post(
            '/api/auth/register/',
            {
                'username': 'amina',
                'name': 'Amina Bello',
                'email': 'amina@example.com',
                'password': 'strongpass123',
                'phone_number': '+2348012345678',
                'address': '12 Unity Road, Ilorin',
                'latitude': 8.4966,
                'longitude': 4.5421,
            },
            format='json',
        )
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)

        login_response = self.client.post(
            '/api/auth/login/',
            {'username': 'amina', 'password': 'strongpass123'},
            format='json',
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}")

        profile_response = self.client.get('/api/users/me/')
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_response.data['username'], 'amina')

        address_response = self.client.post(
            '/api/users/me/addresses/',
            {
                'label': 'Home',
                'full_address': '12 Unity Road, Ilorin',
                'latitude': 8.4966,
                'longitude': 4.5421,
                'is_default': True,
            },
            format='json',
        )
        self.assertEqual(address_response.status_code, status.HTTP_201_CREATED)

        update_response = self.client.put(
            '/api/users/me/',
            {'name': 'Amina K. Bello', 'phone_number': '+2348099999999'},
            format='json',
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data['user']['name'], 'Amina K. Bello')

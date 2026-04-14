from decimal import Decimal

from geopy.distance import geodesic
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsVendor
from orders.models import Review

from .models import VendorProfile
from .serializers import VendorAvailabilitySerializer, VendorProfileSerializer, VendorRegistrationSerializer, VendorScheduleSerializer


class VendorListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = VendorProfile.objects.select_related('user').filter(available=True)
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        radius_km = Decimal(request.query_params.get('radius_km', '10'))

        vendors = []
        for profile in queryset:
            distance_km = None
            if lat is not None and lng is not None:
                distance = geodesic(
                    (float(lat), float(lng)),
                    (profile.service_area_latitude, profile.service_area_longitude),
                ).km
                distance_km = round(distance, 2)
                if Decimal(str(distance_km)) > radius_km:
                    continue
            profile.distance_km = distance_km
            vendors.append(profile)

        vendors.sort(key=lambda item: (item.distance_km is None, item.distance_km or 0, item.business_name.lower()))
        return Response({'vendors': VendorProfileSerializer(vendors, many=True).data, 'total': len(vendors)})


class VendorDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, vendor_id):
        profile = VendorProfile.objects.select_related('user').filter(user_id=vendor_id).first()
        if profile is None:
            return Response({'detail': 'Vendor not found.'}, status=status.HTTP_404_NOT_FOUND)
        data = VendorProfileSerializer(profile).data
        data['reviews'] = [
            {
                'id': review.id,
                'rating': review.rating,
                'comment': review.comment,
                'user_name': review.user.get_full_name() or review.user.username,
                'created_at': review.created_at,
            }
            for review in Review.objects.select_related('user').filter(vendor_id=vendor_id)[:10]
        ]
        return Response(data)


class VendorRegistrationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = VendorRegistrationSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()
        return Response(
            {'vendor_id': profile.user_id, 'status': profile.verification_status},
            status=status.HTTP_201_CREATED,
        )


class VendorAvailabilityView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsVendor]

    def patch(self, request):
        profile = getattr(request.user, 'vendor_profile', None)
        if profile is None:
            return Response({'detail': 'Vendor profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = VendorAvailabilitySerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class VendorScheduleView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsVendor]

    def put(self, request):
        profile = getattr(request.user, 'vendor_profile', None)
        if profile is None:
            return Response({'detail': 'Vendor profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = VendorScheduleSerializer(profile, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Schedule updated'})


class VendorReviewListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, vendor_id):
        reviews = Review.objects.select_related('user').filter(vendor_id=vendor_id)
        average = round(sum(review.rating for review in reviews) / len(reviews), 2) if reviews else 0
        data = [
            {
                'id': review.id,
                'user_name': review.user.get_full_name() or review.user.username,
                'rating': review.rating,
                'comment': review.comment,
                'created_at': review.created_at,
            }
            for review in reviews
        ]
        return Response({'average_rating': average, 'review_count': len(data), 'reviews': data})
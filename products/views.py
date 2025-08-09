from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import WaterType
from .serializers import WaterTypeSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication  # Use this
from accounts.models import User  # Ensure User is imported for VendorListView

class WaterTypeView(APIView):
    authentication_classes = [JWTAuthentication]
    
    def get(self, request):
        water_types = WaterType.objects.filter(vendor=request.user)
        serializer = WaterTypeSerializer(water_types, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        if request.user.user_type != 'vendor':
            return Response({'error': 'Only vendors can create water types'}, status=status.HTTP_403_FORBIDDEN)
        serializer = WaterTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(vendor=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VendorListView(APIView):
    authentication_classes = [JWTAuthentication]
    
    def get(self, request):
        vendors = User.objects.filter(user_type='vendor')
        water_types = WaterType.objects.all()
        serializer = WaterTypeSerializer(water_types, many=True)
        return Response(serializer.data)
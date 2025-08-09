from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order
from .serializers import OrderSerializer
from accounts.models import User
from accounts.authentication import CustomJWTAuthentication

class OrderView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    
    def post(self, request):
        serializer = OrderSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            order = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RiderAssignmentView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    
    def post(self, request, order_id):
        if request.user.user_type != 'vendor':
            return Response({'error': 'Only vendors can assign riders'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            order = Order.objects.get(id=order_id)
            rider_id = request.data.get('rider_id')
            rider = User.objects.get(id=rider_id, user_type='rider')
            order.rider = rider
            order.status = 'assigned'
            order.save()
            return Response(OrderSerializer(order).data)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({'error': 'Rider not found'}, status=status.HTTP_404_NOT_FOUND)
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsVendor

from .models import Order
from .serializers import DisputeCreateSerializer, OrderCancelSerializer, OrderCreateSerializer, OrderReadSerializer, OrderStatusUpdateSerializer, ReviewCreateSerializer


def get_order_for_actor(user, order_id):
    queryset = Order.objects.select_related('delivery_address', 'vendor__vendor_profile', 'user')
    if user.user_type == 'vendor':
        return queryset.filter(pk=order_id, vendor=user).first()
    return queryset.filter(pk=order_id, user=user).first()


class OrderListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = Order.objects.select_related('delivery_address', 'vendor__vendor_profile')
        if request.user.user_type == 'vendor':
            queryset = queryset.filter(vendor=request.user)
        else:
            queryset = queryset.filter(user=request.user)

        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return Response({'orders': OrderReadSerializer(queryset, many=True).data, 'total': queryset.count()})

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(OrderReadSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, order_id):
        order = get_order_for_actor(request.user, order_id)
        if order is None:
            return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(OrderReadSerializer(order).data)


class OrderStatusUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsVendor]

    def patch(self, request, order_id):
        order = get_order_for_actor(request.user, order_id)
        if order is None:
            return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = OrderStatusUpdateSerializer(data=request.data, context={'order': order})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'order_id': order.id, 'status': order.status})


class OrderConfirmDeliveryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        order = get_order_for_actor(request.user, order_id)
        if order is None:
            return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
        if order.user_id != request.user.id:
            return Response({'detail': 'Only the ordering user can confirm delivery.'}, status=status.HTTP_403_FORBIDDEN)
        if order.status != 'delivered':
            return Response({'detail': 'Order must be delivered before confirmation.'}, status=status.HTTP_400_BAD_REQUEST)
        order.status = 'confirmed'
        order.confirmed_at = timezone.now()
        order.save(update_fields=['status', 'confirmed_at', 'updated_at'])
        return Response({'message': 'Delivery confirmed. Payment released to vendor.'})


class OrderCancelView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        order = get_order_for_actor(request.user, order_id)
        if order is None:
            return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
        if order.status in {'delivered', 'confirmed', 'cancelled'}:
            return Response({'detail': 'This order can no longer be cancelled.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = OrderCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order.status = 'cancelled'
        order.cancellation_reason = serializer.validated_data['reason']
        order.save(update_fields=['status', 'cancellation_reason', 'updated_at'])
        if order.vendor_id and hasattr(order.vendor, 'vendor_profile'):
            profile = order.vendor.vendor_profile
            profile.available_litres += order.quantity
            profile.available = True
            profile.save(update_fields=['available_litres', 'available'])
        return Response({'order_id': order.id, 'status': order.status, 'refund_initiated': order.payment_method != 'cash_on_delivery'})


class OrderReviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        order = get_order_for_actor(request.user, order_id)
        if order is None:
            return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ReviewCreateSerializer(data=request.data, context={'request': request, 'order': order})
        serializer.is_valid(raise_exception=True)
        review = serializer.save()
        return Response({'review_id': review.id, 'message': 'Review submitted'}, status=status.HTTP_201_CREATED)


class OrderDisputeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        order = get_order_for_actor(request.user, order_id)
        if order is None:
            return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = DisputeCreateSerializer(data=request.data, context={'request': request, 'order': order})
        serializer.is_valid(raise_exception=True)
        dispute = serializer.save()
        return Response(
            {'dispute_id': dispute.id, 'status': dispute.status, 'message': 'Dispute raised. Admin will review within 24 hours.'},
            status=status.HTTP_201_CREATED,
        )
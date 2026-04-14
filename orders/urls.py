from django.urls import path

from .views import OrderCancelView, OrderConfirmDeliveryView, OrderDetailView, OrderDisputeView, OrderListCreateView, OrderReviewView, OrderStatusUpdateView


urlpatterns = [
    path('', OrderListCreateView.as_view(), name='order-list-create'),
    path('<int:order_id>/', OrderDetailView.as_view(), name='order-detail'),
    path('<int:order_id>/status/', OrderStatusUpdateView.as_view(), name='order-status-update'),
    path('<int:order_id>/confirm-delivery/', OrderConfirmDeliveryView.as_view(), name='order-confirm-delivery'),
    path('<int:order_id>/cancel/', OrderCancelView.as_view(), name='order-cancel'),
    path('<int:order_id>/review/', OrderReviewView.as_view(), name='order-review'),
    path('<int:order_id>/dispute/', OrderDisputeView.as_view(), name='order-dispute'),
]
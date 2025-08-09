from django.urls import path
from .views import OrderView, RiderAssignmentView

urlpatterns = [
    path('', OrderView.as_view(), name='order-create'),
    path('<int:order_id>/assign-rider/', RiderAssignmentView.as_view(), name='assign-rider'),
]
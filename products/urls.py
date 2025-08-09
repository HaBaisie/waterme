from django.urls import path
from .views import WaterTypeView, VendorListView

urlpatterns = [
    path('water-types/', WaterTypeView.as_view(), name='water-types'),
    path('vendors/', VendorListView.as_view(), name='vendor-list'),
]
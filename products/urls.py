from django.urls import path

from .views import VendorAvailabilityView, VendorDetailView, VendorListView, VendorRegistrationView, VendorReviewListView, VendorScheduleView


urlpatterns = [
    path('', VendorListView.as_view(), name='vendor-list'),
    path('register/', VendorRegistrationView.as_view(), name='vendor-register'),
    path('me/availability/', VendorAvailabilityView.as_view(), name='vendor-availability'),
    path('me/schedule/', VendorScheduleView.as_view(), name='vendor-schedule'),
    path('<int:vendor_id>/', VendorDetailView.as_view(), name='vendor-detail'),
    path('<int:vendor_id>/reviews/', VendorReviewListView.as_view(), name='vendor-reviews'),
]
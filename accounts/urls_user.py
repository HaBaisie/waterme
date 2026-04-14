from django.urls import path

from .views import AddressDetailView, AddressListCreateView, CurrentUserView


urlpatterns = [
    path('me/', CurrentUserView.as_view(), name='current-user'),
    path('me/addresses/', AddressListCreateView.as_view(), name='address-create'),
    path('me/addresses/<int:address_id>/', AddressDetailView.as_view(), name='address-delete'),
]
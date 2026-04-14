from django.contrib import admin

from .models import VendorProfile, WaterType


@admin.register(VendorProfile)
class VendorProfileAdmin(admin.ModelAdmin):
	list_display = ('business_name', 'user', 'available', 'available_litres', 'verification_status')
	list_filter = ('available', 'verification_status')
	search_fields = ('business_name', 'user__username', 'user__phone_number')


@admin.register(WaterType)
class WaterTypeAdmin(admin.ModelAdmin):
	list_display = ('name', 'vendor', 'type', 'price', 'size')
	list_filter = ('type',)
	search_fields = ('name', 'vendor__username')
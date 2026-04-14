from django.contrib import admin

from .models import Address, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
	list_display = ('username', 'email', 'user_type', 'phone_number', 'wallet_balance')
	list_filter = ('user_type',)
	search_fields = ('username', 'email', 'phone_number')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
	list_display = ('user', 'label', 'full_address', 'is_default')
	list_filter = ('is_default',)
	search_fields = ('user__username', 'label', 'full_address')
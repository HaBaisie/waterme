from django.contrib import admin

from .models import Dispute, Order, Review


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'vendor', 'status', 'quantity', 'total_amount', 'created_at')
	list_filter = ('status', 'payment_method')
	search_fields = ('user__username', 'vendor__username', 'payment_reference')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
	list_display = ('id', 'order', 'vendor', 'rating', 'created_at')
	list_filter = ('rating',)


@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
	list_display = ('id', 'order', 'user', 'reason', 'status', 'created_at')
	list_filter = ('reason', 'status')
from django.contrib import admin
from django.utils.html import format_html
from .models import Artwork, Order, CustomOrder

@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'title', 'category', 'price', 'is_available', 'created_at')
    list_filter = ('category', 'is_available')
    search_fields = ('title', 'description')
    list_editable = ('price', 'is_available')
    
    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />', obj.image.url)
        return "No Image"
    thumbnail.short_description = 'Preview'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'customer_name', 'artwork', 'total_price', 'payment_method', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_method', 'payment_status', 'created_at')
    search_fields = ('order_id', 'customer_name', 'email', 'phone', 'transaction_id')
    readonly_fields = ('order_id', 'total_price', 'created_at', 'screenshot_preview')
    actions = ['mark_as_paid', 'mark_as_failed']
    
    fieldsets = (
        ('Order Info', {
            'fields': ('order_id', 'artwork', 'quantity', 'total_price', 'status', 'created_at')
        }),
        ('Payment Info', {
            'fields': ('payment_method', 'payment_status', 'transaction_id', 'payment_screenshot', 'screenshot_preview')
        }),
        ('Customer Info', {
            'fields': ('customer_name', 'email', 'phone', 'address')
        }),
    )

    def screenshot_preview(self, obj):
        if obj.payment_screenshot:
            return format_html('<a href="{}" target="_blank"><img src="{}" style="width: 200px; height: auto;" /></a>', obj.payment_screenshot.url, obj.payment_screenshot.url)
        return "No Screenshot"
    screenshot_preview.short_description = 'Screenshot'

    def mark_as_paid(self, request, queryset):
        queryset.update(payment_status='Paid', status='Confirmed')
    mark_as_paid.short_description = "Mark selected orders as Paid"

    def mark_as_failed(self, request, queryset):
        queryset.update(payment_status='Failed')
    mark_as_failed.short_description = "Mark selected orders as Failed"

@admin.register(CustomOrder)
class CustomOrderAdmin(admin.ModelAdmin):
    list_display = ('tracking_id', 'name', 'email', 'status', 'final_price', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status', 'created_at', 'size')
    search_fields = ('name', 'email', 'phone', 'description')
    list_editable = ('status', 'payment_status')
    readonly_fields = ('created_at', 'updated_at', 'estimated_price', 'reference_preview_large')
    
    fieldsets = (
        ('Internal Tracking', {
            'fields': (('status', 'payment_status'), ('estimated_price', 'final_price'), 'is_price_confirmed')
        }),
        ('Customer Info', {
            'fields': (('name', 'email', 'phone'),)
        }),
        ('Project Requirements', {
            'fields': ('art_type', ('size', 'detail_level'), 'color_preference', 'description', 'deadline')
        }),
        ('Visuals', {
            'fields': ('reference_image', 'reference_preview_large')
        }),
        ('System Metadata', {
            'fields': (('created_at', 'updated_at'),)
        }),
    )

    def reference_preview_large(self, obj):
        if obj.reference_image:
            return format_html('<a href="{}" target="_blank"><img src="{}" style="max-width: 400px; height: auto; border-radius: 12px; border: 1px solid #eee;" /></a>', obj.reference_image.url, obj.reference_image.url)
        return "No reference image uploaded."
    reference_preview_large.short_description = 'Reference Preview'

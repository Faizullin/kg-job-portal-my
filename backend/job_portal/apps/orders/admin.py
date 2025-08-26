from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count
from .models import Order, OrderAddon, OrderPhoto, Bid, OrderAssignment, OrderDispute


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'title', 'client', 'service_subcategory', 'status', 'budget_display',
        'service_date', 'created_at', 'addons_count'
    ]
    list_filter = ['status', 'service_subcategory', 'created_at', 'service_date', 'urgency']
    search_fields = ['title', 'description', 'location', 'client__user_profile__user__first_name']
    ordering = ['-created_at']
    list_editable = ['status']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('title', 'description', 'status', 'service_subcategory')
        }),
        ('Client & Service', {
            'fields': ('client', 'service_subcategory')
        }),
        ('Schedule & Location', {
            'fields': ('service_date', 'service_time', 'urgency', 'location', 'city', 'state', 'country', 'postal_code')
        }),
        ('Budget', {
            'fields': ('budget_min', 'budget_max', 'final_price')
        }),
        ('Additional Information', {
            'fields': ('attachments', 'special_requirements', 'is_featured')
        }),
    )
    
    def budget_display(self, obj):
        if obj.budget_min and obj.budget_max:
            return f"${obj.budget_min:.2f} - ${obj.budget_max:.2f}"
        elif obj.budget_min:
            return f"Min: ${obj.budget_min:.2f}"
        elif obj.budget_max:
            return f"Max: ${obj.budget_max:.2f}"
        return "Not specified"
    budget_display.short_description = 'Budget Range'
    
    def addons_count(self, obj):
        return obj.order_addons.count()
    addons_count.short_description = 'Add-ons'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'client__user_profile__user', 'service_subcategory'
        )


@admin.register(OrderAddon)
class OrderAddonAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'order', 'addon', 'quantity', 'price', 'total_price_display'
    ]
    list_filter = ['order__status', 'created_at']
    search_fields = ['order__title', 'addon__name']
    ordering = ['-created_at']
    list_editable = ['quantity', 'price']
    
    fieldsets = (
        ('Addon Information', {
            'fields': ('order', 'addon', 'quantity', 'price')
        }),
    )
    
    def total_price_display(self, obj):
        return f"${obj.quantity * obj.price:.2f}"
    total_price_display.short_description = 'Total Price'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order', 'addon')


@admin.register(OrderPhoto)
class OrderPhotoAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'order', 'photo_preview', 'caption', 'is_primary', 'created_at'
    ]
    list_filter = ['is_primary', 'created_at']
    search_fields = ['order__title', 'caption']
    ordering = ['-is_primary', '-created_at']
    list_editable = ['is_primary']
    
    fieldsets = (
        ('Photo Information', {
            'fields': ('order', 'photo_url', 'caption', 'is_primary')
        }),
    )
    
    def photo_preview(self, obj):
        if obj.photo_url:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.photo_url)
        return 'No photo'
    photo_preview.short_description = 'Photo'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order')


@admin.register(OrderDispute)
class OrderDisputeAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'order', 'dispute_type', 'status', 'description_preview',
        'created_at', 'resolved_at', 'days_open'
    ]
    list_filter = ['dispute_type', 'status', 'created_at']
    search_fields = ['order__title', 'description', 'admin_notes']
    ordering = ['-created_at']
    list_editable = ['status']
    
    fieldsets = (
        ('Dispute Information', {
            'fields': ('order', 'raised_by', 'dispute_type', 'description', 'evidence')
        }),
        ('Resolution', {
            'fields': ('status', 'admin_notes', 'resolved_by', 'resolved_at', 'resolution')
        }),
    )
    
    def description_preview(self, obj):
        if obj.description:
            return obj.description[:100] + '...' if len(obj.description) > 100 else obj.description
        return '-'
    description_preview.short_description = 'Description'
    
    def days_open(self, obj):
        if obj.resolved_at:
            delta = obj.resolved_at - obj.created_at
            return delta.days
        else:
            from django.utils import timezone
            delta = timezone.now() - obj.created_at
            return delta.days
    days_open.short_description = 'Days Open'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order', 'raised_by', 'resolved_by')


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'order', 'provider', 'amount', 'status', 'estimated_duration', 'created_at'
    ]
    list_filter = ['status', 'created_at', 'is_negotiable']
    search_fields = ['order__title', 'provider__user_profile__user__first_name', 'description']
    ordering = ['-created_at']
    list_editable = ['status']
    
    fieldsets = (
        ('Bid Information', {
            'fields': ('order', 'provider', 'amount', 'description', 'estimated_duration')
        }),
        ('Status & Terms', {
            'fields': ('status', 'is_negotiable', 'terms_conditions')
        }),
        ('Timestamps', {
            'fields': ('accepted_at', 'rejected_at', 'withdrawn_at')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order', 'provider__user_profile__user')


@admin.register(OrderAssignment)
class OrderAssignmentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'order', 'provider', 'assigned_at', 'start_date', 'client_rating'
    ]
    list_filter = ['assigned_at', 'start_date', 'created_at']
    search_fields = ['order__title', 'provider__user_profile__user__first_name']
    ordering = ['-assigned_at']
    
    fieldsets = (
        ('Assignment Information', {
            'fields': ('order', 'provider', 'accepted_bid')
        }),
        ('Schedule', {
            'fields': ('start_date', 'start_time')
        }),
        ('Progress', {
            'fields': ('progress_notes', 'completion_notes')
        }),
        ('Client Feedback', {
            'fields': ('client_rating', 'client_review')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order', 'provider__user_profile__user', 'accepted_bid')

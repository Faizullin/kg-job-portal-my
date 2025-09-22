from django.contrib import admin
from .models import Order, Bid, OrderAssignment, OrderDispute, OrderAttachment


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'title', 'client', 'service_subcategory', 'status', 'budget_display',
        'service_date', 'created_at'
    ]
    list_filter = ['status', 'service_subcategory', 'created_at', 'service_date', 'urgency']
    search_fields = ['title', 'description', 'location', 'client__user_profile__user__first_name']
    ordering = ['-created_at']
    list_editable = ['status']
    raw_id_fields = ['client', 'service_subcategory']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('title', 'description', 'status', 'service_subcategory')
        }),
        ('Client & Service', {
            'fields': ('client',)
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
    
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'client__user_profile__user', 'service_subcategory'
        )


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
    raw_id_fields = ['order', 'raised_by', 'resolved_by']
    
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
    raw_id_fields = ['order', 'provider']
    
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
        return super().get_queryset(request).select_related('order', 'provider__user_profile')


@admin.register(OrderAssignment)
class OrderAssignmentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'order', 'provider', 'assigned_at', 'start_date', 'client_rating'
    ]
    list_filter = ['assigned_at', 'start_date', 'created_at']
    search_fields = ['order__title', 'provider__user_profile__user__first_name']
    ordering = ['-assigned_at']
    raw_id_fields = ['order', 'provider', 'accepted_bid']
    
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
        return super().get_queryset(request).select_related('order', 'provider__user_profile', 'accepted_bid')


@admin.register(OrderAttachment)
class OrderAttachmentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'file_name', 'file_type', 'file_size', 'uploaded_by', 'created_at'
    ]
    list_filter = ['file_type', 'created_at']
    search_fields = ['file_name', 'description', 'uploaded_by__first_name']
    ordering = ['-created_at']
    raw_id_fields = ['uploaded_by']
    
    fieldsets = (
        ('File Information', {
            'fields': ('file_name', 'file_type', 'file_size', 'file_url', 'mime_type')
        }),
        ('Details', {
            'fields': ('description', 'uploaded_by')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('uploaded_by')

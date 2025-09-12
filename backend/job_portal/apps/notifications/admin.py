from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Q
from .models import NotificationTemplate, UserNotification, NotificationDelivery, NotificationPreference, NotificationQueue


@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'subject_preview', 'status', 'priority',
        'is_read', 'created_at', 'read_at'
    ]
    list_filter = ['status', 'priority', 'is_read', 'created_at']
    search_fields = ['subject', 'message', 'user__first_name', 'user__last_name']
    ordering = ['-created_at']
    list_editable = ['is_read']
    raw_id_fields = ['user', 'template']
    
    fieldsets = (
        ('Notification Information', {
            'fields': ('user', 'template', 'subject', 'message', 'short_message', 'priority')
        }),
        ('Content & Data', {
            'fields': ('context_data', 'related_object_type', 'related_object_id')
        }),
        ('Status', {
            'fields': ('status', 'is_read', 'read_at')
        }),
        ('Delivery Tracking', {
            'fields': ('sent_at', 'delivered_at', 'failed_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def subject_preview(self, obj):
        if obj.subject:
            return obj.subject[:50] + '...' if len(obj.subject) > 50 else obj.subject
        return '-'
    subject_preview.short_description = 'Subject'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'template')


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'name', 'notification_type', 'subject_preview', 'is_active',
        'variables_count', 'created_at'
    ]
    list_filter = ['notification_type', 'is_active', 'created_at']
    search_fields = ['name', 'subject', 'content']
    ordering = ['name']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Template Information', {
            'fields': ('name', 'notification_type', 'is_active')
        }),
        ('Content', {
            'fields': ('subject', 'content')
        }),
        ('Variables', {
            'fields': ('variables',),
            'classes': ('collapse',)
        }),
    )
    
    def subject_preview(self, obj):
        if obj.subject:
            return obj.subject[:50] + '...' if len(obj.subject) > 50 else obj.subject
        return '-'
    subject_preview.short_description = 'Subject'
    
    def variables_count(self, obj):
        if obj.variables:
            return len(obj.variables)
        return 0
    variables_count.short_description = 'Variables'


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'email_notifications', 'push_notifications',
        'sms_notifications', 'digest_frequency', 'timezone'
    ]
    list_filter = ['email_notifications', 'push_notifications', 'sms_notifications', 'digest_frequency']
    search_fields = ['user__first_name', 'user__last_name']
    ordering = ['user__first_name']
    list_editable = ['email_notifications', 'push_notifications', 'sms_notifications']
    raw_id_fields = ['user']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('General Preferences', {
            'fields': ('email_notifications', 'push_notifications', 'sms_notifications', 'in_app_notifications')
        }),
        ('Specific Notifications', {
            'fields': ('order_updates', 'bid_notifications', 'payment_notifications', 'chat_notifications', 'promotional_notifications', 'system_notifications')
        }),
        ('Timing Preferences', {
            'fields': ('quiet_hours_start', 'quiet_hours_end', 'timezone')
        }),
        ('Frequency', {
            'fields': ('digest_frequency',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

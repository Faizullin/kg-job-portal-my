from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Q
from .models import NotificationTemplate, UserNotification, NotificationDelivery, NotificationPreference, NotificationLog, NotificationQueue


@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user_profile', 'title_preview', 'notification_type', 'priority',
        'is_read', 'created_at', 'read_at'
    ]
    list_filter = ['notification_type', 'priority', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'user_profile__user__first_name', 'user_profile__user__last_name']
    ordering = ['-created_at']
    list_editable = ['is_read']
    
    fieldsets = (
        ('Notification Information', {
            'fields': ('user_profile', 'title', 'message', 'notification_type', 'priority')
        }),
        ('Content & Data', {
            'fields': ('data', 'action_url')
        }),
        ('Status', {
            'fields': ('is_read', 'read_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def title_preview(self, obj):
        if obj.title:
            return obj.title[:50] + '...' if len(obj.title) > 50 else obj.title
        return '-'
    title_preview.short_description = 'Title'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user_profile__user')


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
        'id', 'user_profile', 'notification_type', 'email_enabled', 'push_enabled',
        'sms_enabled', 'frequency', 'is_active'
    ]
    list_filter = ['notification_type', 'email_enabled', 'push_enabled', 'sms_enabled', 'frequency', 'is_active']
    search_fields = ['user_profile__user__first_name', 'user_profile__user__last_name']
    ordering = ['user_profile__user__first_name', 'notification_type']
    list_editable = ['email_enabled', 'push_enabled', 'sms_enabled', 'is_active']
    
    fieldsets = (
        ('User & Type', {
            'fields': ('user_profile', 'notification_type')
        }),
        ('Delivery Methods', {
            'fields': ('email_enabled', 'push_enabled', 'sms_enabled')
        }),
        ('Settings', {
            'fields': ('frequency', 'is_active')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user_profile__user')


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'notification', 'user', 'status', 'delivery_method',
        'sent_at', 'delivered_at', 'error_message_preview'
    ]
    list_filter = ['status', 'delivery_method', 'sent_at', 'delivered_at']
    search_fields = ['notification__title', 'user__first_name', 'error_message']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Log Information', {
            'fields': ('notification', 'user', 'status', 'delivery_method')
        }),
        ('Timestamps', {
            'fields': ('sent_at', 'delivered_at')
        }),
        ('Error Details', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
    )
    
    def error_message_preview(self, obj):
        if obj.error_message:
            return obj.error_message[:100] + '...' if len(obj.error_message) > 100 else obj.error_message
        return '-'
    error_message_preview.short_description = 'Error Message'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('notification', 'user')

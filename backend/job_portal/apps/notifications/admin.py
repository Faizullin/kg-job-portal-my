from django.contrib import admin
from django.utils.html import format_html
from .models import UserNotification


@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'title_preview', 'notification_type',
        'is_read', 'created_at', 'read_at'
    ]
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'user__first_name', 'user__last_name']
    ordering = ['-created_at']
    list_editable = ['is_read']
    raw_id_fields = ['user', 'order', 'bid']
    
    fieldsets = (
        ('Notification Information', {
            'fields': ('user', 'title', 'message', 'notification_type')
        }),
        ('Related Objects', {
            'fields': ('order', 'bid')
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
        return super().get_queryset(request).select_related('user', 'order', 'bid')
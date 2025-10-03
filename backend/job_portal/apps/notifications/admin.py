from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'recipient',  'title_preview',
        'is_read',
    ]
    list_filter = ['is_read', 'created_at']
    ordering = ['-created_at']
    list_editable = ['is_read']
    raw_id_fields = ['recipient']

    def title_preview(self, obj):
        if obj.title:
            return obj.title[:50] + '...' if len(obj.title) > 50 else obj.title
        return '-'

    title_preview.short_description = 'Title'

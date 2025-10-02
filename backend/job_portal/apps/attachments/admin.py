from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.utils.translation import gettext_lazy as _

from .models import Attachment


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    """Admin interface for Attachment model."""
    
    list_display = [
        'original_filename', 
        'content_type', 
        'object_id', 
        'file_type', 
        'size', 
        'uploaded_by', 
        'is_public', 
        'created_at'
    ]
    list_filter = [
        'file_type', 
        'is_public', 
        'content_type', 
        'created_at',
        'uploaded_by'
    ]
    search_fields = [
        'original_filename', 
        'description', 
        'uploaded_by__username', 
        'uploaded_by__email'
    ]
    readonly_fields = [
        'size', 
        'mime_type', 
        'file_type', 
        'created_at', 
        'updated_at'
    ]
    fieldsets = (
        (_('File Information'), {
            'fields': ('file', 'original_filename', 'size', 'file_type', 'mime_type')
        }),
        (_('Content Association'), {
            'fields': ('content_type', 'object_id')
        }),
        (_('Upload Information'), {
            'fields': ('uploaded_by', 'description', 'is_public')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'content_type', 
            'uploaded_by'
        )


class AttachmentInline(GenericTabularInline):
    """Generic inline for attachments."""
    model = Attachment
    extra = 0
    fields = ('file', 'original_filename', 'file_type', 'uploaded_by', 'is_public')
    readonly_fields = ('size', 'mime_type', 'file_type')

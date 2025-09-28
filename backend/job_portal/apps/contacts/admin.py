from django.contrib import admin
from .models import SimpleContact


@admin.register(SimpleContact)
class SimpleContactAdmin(admin.ModelAdmin):
    list_display = [
        'first_name', 'last_name', 'email', 'subject', 'enquiry_type', 
        'created_at'
    ]
    list_filter = ['enquiry_type', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'subject', 'message']
    ordering = ['-created_at']
    list_editable = ['enquiry_type']
    raw_id_fields = ['user']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Message Details', {
            'fields': ('subject', 'message', 'enquiry_type')
        }),
        ('System Information', {
            'fields': ('user', 'ip_address'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['ip_address', 'created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

from django.contrib import admin
from .models import MasterResume


@admin.register(MasterResume)
class MasterResumeAdmin(admin.ModelAdmin):
    list_display = ['title', 'master', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'content', 'master__user__username']
    ordering = ['-created_at']
    list_editable = ['status']
    raw_id_fields = ['master']
    
    fieldsets = (
        ('Resume Information', {
            'fields': ('master', 'title', 'content', 'status')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('master__user')

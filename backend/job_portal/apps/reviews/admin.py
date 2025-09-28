from django.contrib import admin
from django.utils.html import format_html
from .models import Review, AppFeedback


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'job', 'reviewer', 'master', 'rating', 'is_verified', 'is_deleted',
        'created_at'
    ]
    list_filter = ['rating', 'is_verified', 'is_deleted', 'created_at']
    search_fields = ['job__title', 'reviewer__first_name', 'reviewer__last_name', 'master__user__first_name']
    ordering = ['-created_at']
    list_editable = ['is_verified', 'is_deleted']
    raw_id_fields = ['job', 'reviewer', 'master']
    
    fieldsets = (
        ('Review Information', {
            'fields': ('job', 'reviewer', 'master', 'rating')
        }),
        ('Review Content', {
            'fields': ('title', 'comment')
        }),
        ('Status & Verification', {
            'fields': ('is_verified', 'is_deleted'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'job', 'reviewer', 'master__user'
        )


@admin.register(AppFeedback)
class AppFeedbackAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'rating', 'platform', 'is_reviewed',
        'created_at'
    ]
    list_filter = ['rating', 'platform', 'is_reviewed', 'created_at']
    search_fields = ['user__username', 'user__email', 'detailed_feedback']
    ordering = ['-created_at']
    list_editable = ['is_reviewed']
    raw_id_fields = ['user']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'rating')
        }),
        ('Feedback Content', {
            'fields': ('detailed_feedback', 'general_opinion')
        }),
        ('Feedback Categories', {
            'fields': ('design_feedback', 'usability_feedback', 'bug_report', 'missing_features', 'everything_satisfies')
        }),
        ('Technical Information', {
            'fields': ('app_version', 'device_info', 'platform')
        }),
        ('Admin Processing', {
            'fields': ('is_reviewed', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

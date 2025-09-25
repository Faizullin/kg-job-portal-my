from django.contrib import admin
from django.utils.html import format_html
from .models import Review, AppFeedback


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'order', 'reviewer', 'provider', 'overall_rating', 'is_verified',
        'created_at'
    ]
    list_filter = ['overall_rating', 'is_verified', 'created_at']
    search_fields = ['order__title', 'reviewer__first_name', 'reviewer__last_name', 'provider__user_profile__user__first_name']
    ordering = ['-created_at']
    list_editable = ['is_verified']
    raw_id_fields = ['order', 'reviewer', 'provider']
    
    fieldsets = (
        ('Review Information', {
            'fields': ('order', 'reviewer', 'provider', 'overall_rating')
        }),
        ('Review Content', {
            'fields': ('title', 'comment')
        }),
        ('Verification', {
            'fields': ('is_verified',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'order', 'reviewer', 'provider__user_profile__user'
        )


@admin.register(AppFeedback)
class AppFeedbackAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'overall_rating', 'platform', 'is_reviewed',
        'created_at'
    ]
    list_filter = ['overall_rating', 'platform', 'is_reviewed', 'created_at']
    search_fields = ['user__username', 'user__email', 'detailed_feedback']
    ordering = ['-created_at']
    list_editable = ['is_reviewed']
    raw_id_fields = ['user']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'overall_rating')
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

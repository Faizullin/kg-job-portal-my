from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from .models import Job, JobApplication, JobDispute, BookmarkJob, FavoriteJob, JobAssignment
from job_portal.apps.attachments.models import Attachment


class AttachmentInline(GenericTabularInline):
    """Generic inline for attachments."""
    model = Attachment
    extra = 0
    fields = ('file', 'original_filename', 'file_type', 'uploaded_by', 'is_public')
    readonly_fields = ('size', 'mime_type', 'file_type')


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'title', 'employer', 'service_subcategory', 'status', 'job_type', 'budget_display',
        'service_date', 'created_at'
    ]
    list_filter = ['status', 'job_type', 'urgency', 'service_subcategory', 'created_at', 'service_date']
    search_fields = ['title', 'description', 'employer__user__first_name', 'employer__user__last_name',
                     "employer__user_username"]
    ordering = ['-created_at']
    list_editable = ['status']
    raw_id_fields = ['employer', 'company', 'service_subcategory', 'city']

    fieldsets = (
        ('Job Information', {
            'fields': ('title', 'description', 'status', 'job_type', 'service_subcategory')
        }),
        ('Employer & Company', {
            'fields': ('employer', 'company')
        }),
        ('Schedule & Location', {
            'fields': ('service_date', 'service_time', 'urgency', 'location', 'city')
        }),
        ('Budget & Pricing', {
            'fields': ('budget_min', 'budget_max', 'final_price')
        }),
        ('Requirements & Skills', {
            'fields': ('special_requirements', 'skills')
        }),
        ('Status & Availability', {
            'fields': ('is_available', 'published_at', 'assigned_at', 'started_at', 'completed_at', 'cancelled_at')
        }),
    )

    filter_horizontal = ['skills']
    inlines = [AttachmentInline]

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
            'employer__user', 'company', 'service_subcategory', 'city'
        )


@admin.register(JobAssignment)
class JobAssignmentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'job', 'master', 'status', 'assigned_at', 'started_at', 'completed_at'
    ]
    list_filter = ['status', 'assigned_at', 'started_at', 'completed_at']
    search_fields = ['job__title', 'master__user__first_name', 'master__user__last_name']
    ordering = ['-assigned_at']
    raw_id_fields = ['job', 'master']
    inlines = [AttachmentInline]

    fieldsets = (
        ('Assignment Information', {
            'fields': ('job', 'master', 'status')
        }),
        ('Timestamps', {
            'fields': ('assigned_at', 'started_at', 'completed_at')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('job', 'master__user')


@admin.register(JobDispute)
class JobDisputeAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'job', 'dispute_type', 'status', 'description_preview',
        'created_at', 'resolved_at', 'days_open'
    ]
    list_filter = ['dispute_type', 'status', 'created_at']
    search_fields = ['job__title', 'description', 'admin_notes']
    ordering = ['-created_at']
    list_editable = ['status']
    raw_id_fields = ['job', 'raised_by', 'resolved_by']

    fieldsets = (
        ('Dispute Information', {
            'fields': ('job', 'raised_by', 'dispute_type', 'description', 'evidence')
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
        return super().get_queryset(request).select_related('job', 'raised_by', 'resolved_by')


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'job', 'applicant', 'amount', 'status', 'estimated_duration', 'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['job__title', 'applicant__user__first_name', 'applicant__user__last_name', 'comment']
    ordering = ['-created_at']
    list_editable = ['status']
    raw_id_fields = ['job', 'applicant', 'resume']

    fieldsets = (
        ('Application Information', {
            'fields': ('job', 'applicant', 'amount', 'comment', 'estimated_duration')
        }),
        ('Resume & Status', {
            'fields': ('resume', 'status')
        }),
        ('Timestamps', {
            'fields': ('applied_at', 'accepted_at', 'rejected_at', 'withdrawn_at')
        }),
    )

    readonly_fields = ['applied_at']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('job', 'applicant__user', 'resume')


@admin.register(BookmarkJob)
class BookmarkJobAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'job', 'created_at'
    ]
    list_filter = ['created_at']
    search_fields = ['user__first_name', 'user__last_name', 'job__title']
    ordering = ['-created_at']
    raw_id_fields = ['user', 'job']

    fieldsets = (
        ('Bookmark Information', {
            'fields': ('user', 'job')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'job')


@admin.register(FavoriteJob)
class FavoriteJobAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'job', 'created_at'
    ]
    list_filter = ['created_at']
    search_fields = ['user__first_name', 'user__last_name', 'job__title']
    ordering = ['-created_at']
    raw_id_fields = ['user', 'job']

    fieldsets = (
        ('Favorite Information', {
            'fields': ('user', 'job')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'job')



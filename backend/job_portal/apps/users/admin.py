from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from .models import (
    Profession, Master, Employer, Skill, MasterSkill, PortfolioItem, 
    Certificate, MasterStatistics, Company
)
from job_portal.apps.attachments.models import Attachment


class AttachmentInline(GenericTabularInline):
    """Generic inline for attachments."""
    model = Attachment
    extra = 0
    fields = ('file', 'original_filename', 'file_type', 'uploaded_by', 'is_public')
    readonly_fields = ('size', 'mime_type', 'file_type')


@admin.register(Profession)
class ProfessionAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    list_editable = ['is_active']
    raw_id_fields = ['category']
    
    fieldsets = (
        ('Profession Information', {
            'fields': ('name', 'description', 'category', 'is_active')
        }),
    )


@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ['user', 'profession', 'is_available', 'is_verified_provider', 'is_top_master', 'get_average_rating', 'get_total_reviews']
    list_filter = ['is_verified_provider', 'is_available', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'profession__name']
    ordering = ['-created_at']
    list_editable = ['is_verified_provider', 'is_available', 'is_top_master']
    raw_id_fields = ['user', 'profession']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'profession')
        }),
        ('Business Details', {
            'fields': ('service_areas', 'services_offered', 'works_remotely', 'accepts_clients_at_location', 'travels_to_clients')
        }),
        ('Pricing & Availability', {
            'fields': ('hourly_rate', 'is_available', 'response_time_hours')
        }),
        ('Professional Information', {
            'fields': ('work_experience_start_year', 'education_institution', 'education_years', 'languages', 'about_description')
        }),
        ('Location & Status', {
            'fields': ('current_location', 'is_online', 'last_seen')
        }),
        ('Verification', {
            'fields': ('is_verified_provider', 'is_top_master')
        }),
    )
    
    def get_average_rating(self, obj):
        if hasattr(obj, 'statistics') and obj.statistics:
            return obj.statistics.average_rating
        return "0.00"
    get_average_rating.short_description = 'Avg Rating'
    
    def get_total_reviews(self, obj):
        if hasattr(obj, 'statistics') and obj.statistics:
            return obj.statistics.total_reviews
        return 0
    get_total_reviews.short_description = 'Total Reviews'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'statistics')


@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_orders', 'completed_orders', 'cancelled_orders']
    list_filter = ['created_at']
    search_fields = ['user__first_name', 'user__last_name']
    ordering = ['-total_orders', '-created_at']
    raw_id_fields = ['user', 'favorite_masters']
    
    fieldsets = (
        ('Client Information', {
            'fields': ('user',)
        }),
        ('Preferences', {
            'fields': ('preferred_services',)
        }),
        ('Order History', {
            'fields': ('total_orders', 'completed_orders', 'cancelled_orders')
        }),
        ('Favorites', {
            'fields': ('favorite_masters',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(MasterStatistics)
class MasterStatisticsAdmin(admin.ModelAdmin):
    list_display = [
        'master', 'total_jobs_completed', 'average_rating', 'total_reviews',
        'on_time_percentage', 'repeat_customer_percentage', 'created_at'
    ]
    list_filter = ['created_at']
    search_fields = ['master__user__first_name', 'master__user__last_name']
    ordering = ['-average_rating', '-total_reviews']
    raw_id_fields = ['master']
    
    fieldsets = (
        ('Master Information', {
            'fields': ('master',)
        }),
        ('Performance Metrics', {
            'fields': ('total_jobs_completed', 'on_time_percentage', 'repeat_customer_percentage')
        }),
        ('Ratings & Reviews', {
            'fields': ('average_rating', 'total_reviews')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('master__user')


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    list_editable = ['is_active']
    raw_id_fields = ['category']
    
    fieldsets = (
        ('Skill Information', {
            'fields': ('name', 'description', 'category', 'is_active')
        }),
    )


@admin.register(MasterSkill)
class MasterSkillAdmin(admin.ModelAdmin):
    list_display = ['master', 'skill', 'proficiency_level', 'years_of_experience', 'is_primary_skill']
    list_filter = ['proficiency_level', 'is_primary_skill', 'created_at']
    search_fields = ['master__user__first_name', 'master__user__last_name', 'skill__name']
    ordering = ['-created_at']
    list_editable = ['proficiency_level', 'years_of_experience', 'is_primary_skill']
    raw_id_fields = ['master', 'skill']
    
    fieldsets = (
        ('Master & Skill', {
            'fields': ('master', 'skill')
        }),
        ('Proficiency Details', {
            'fields': ('proficiency_level', 'years_of_experience', 'is_primary_skill')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('master__user', 'skill')


@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'master', 'skill_used', 'is_featured', 'attachments_count', 'created_at']
    list_filter = ['is_featured', 'skill_used', 'created_at']
    search_fields = ['title', 'description', 'master__user__first_name', 'master__user__last_name']
    ordering = ['-is_featured', '-created_at']
    list_editable = ['is_featured']
    raw_id_fields = ['master', 'skill_used']
    inlines = [AttachmentInline]
    
    fieldsets = (
        ('Portfolio Information', {
            'fields': ('master', 'title', 'description', 'skill_used', 'is_featured')
        }),
    )
    
    def attachments_count(self, obj):
        return obj.attachments.count()
    
    attachments_count.short_description = 'Attachments'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('master__user', 'skill_used')


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['name', 'master', 'issuing_organization', 'issue_date', 'is_verified']
    list_filter = ['is_verified', 'issue_date', 'created_at']
    search_fields = ['name', 'issuing_organization', 'certificate_number', 'master__user__first_name', 'master__user__last_name']
    ordering = ['-issue_date', '-created_at']
    list_editable = ['is_verified']
    raw_id_fields = ['master']
    
    fieldsets = (
        ('Certificate Information', {
            'fields': ('master', 'name', 'issuing_organization', 'certificate_number')
        }),
        ('Dates', {
            'fields': ('issue_date', 'expiry_date')
        }),
        ('Files & Verification', {
            'fields': ('certificate_file', 'is_verified')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('master__user')


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_email', 'website', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description', 'contact_email', 'website']
    ordering = ['name']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Company Information', {
            'fields': ('name', 'description', 'website')
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone', 'address')
        }),
        ('Status', {
            'fields': ('is_active',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()

from django.contrib import admin
from .models import (
    UserModel, 
    UserActivityDateModel, LoginSession
)


@admin.register(UserModel)
class UserModelAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'user_type', 'is_active', 'blocked', 'is_deleted', 'date_joined')
    list_filter = ('user_type', 'is_active', 'blocked', 'is_deleted', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email',  'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email', 'description', 'photo', 'photo_url')
        }),
        ('User Type & Status', {
            'fields': ('user_type', 'blocked', 'is_active', 'is_staff', 'is_superuser')
        }),
        ('Firebase', {
            'fields': ('firebase_user_id',)
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
        ('Soft Delete', {
            'fields': ('is_deleted', 'deleted_at', 'restored_at'),
            'classes': ('collapse',)
        }),
        ('Permissions', {
            'fields': ('groups', 'user_permissions'),
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type'),
        }),
    )
    
    filter_horizontal = ('groups', 'user_permissions')
    
    actions = ['restore_users', 'hard_delete_users']
    
    def restore_users(self, request, queryset):
        """Restore soft-deleted users"""
        restored_count = 0
        for user in queryset:
            user.restore()
            restored_count += 1
        
        if restored_count == 1:
            message = '1 user was successfully restored.'
        else:
            message = f'{restored_count} users were successfully restored.'
        
        self.message_user(request, message)
    
    restore_users.short_description = "Restore selected users"
    
    def hard_delete_users(self, request, queryset):
        """Permanently delete users"""
        deleted_count = queryset.count()
        queryset.delete()
        
        if deleted_count == 1:
            message = '1 user was permanently deleted.'
        else:
            message = f'{deleted_count} users were permanently deleted.'
        
        self.message_user(request, message)
    
    hard_delete_users.short_description = "Permanently delete selected users"


@admin.register(UserActivityDateModel)
class UserActivityDateModelAdmin(admin.ModelAdmin):
    list_display = ('user', 'datetime')
    list_filter = ('datetime',)
    search_fields = ('user__username', 'user__email')
    ordering = ('-datetime',)


@admin.register(LoginSession)
class LoginSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_key', 'ip_address', 'login_at', 'is_active')
    list_filter = ('is_active', 'login_at')
    search_fields = ('user__username', 'user__email', 'session_key')
    ordering = ('-login_at',)

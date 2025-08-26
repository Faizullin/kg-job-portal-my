from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Max, Q
from .models import ChatRoom, ChatMessage, ChatParticipant, ChatTemplate, ChatNotification, ChatReport


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'title', 'chat_type', 'order', 'participants_count', 'messages_count',
        'last_message_at', 'created_at'
    ]
    list_filter = ['chat_type', 'created_at']
    search_fields = ['title', 'order__title']
    ordering = ['-created_at']
    raw_id_fields = ['order']
    
    fieldsets = (
        ('Room Information', {
            'fields': ('title', 'chat_type', 'order')
        }),
        ('Status', {
            'fields': ('is_active', 'last_message_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def participants_count(self, obj):
        return obj.participants.count()
    participants_count.short_description = 'Participants'
    
    def messages_count(self, obj):
        return obj.messages.count()
    messages_count.short_description = 'Messages'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order').annotate(
            participants_count=Count('participants'),
            messages_count=Count('messages')
        )


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'chat_room', 'sender', 'content_preview', 'message_type',
        'is_read', 'attachment_info', 'created_at'
    ]
    list_filter = ['message_type', 'is_read', 'created_at']
    search_fields = ['content', 'sender__first_name', 'chat_room__name']
    ordering = ['-created_at']
    list_editable = ['is_read']
    raw_id_fields = ['chat_room', 'sender', 'reply_to']
    
    fieldsets = (
        ('Message Information', {
            'fields': ('chat_room', 'sender', 'content', 'message_type')
        }),
        ('Attachments', {
            'fields': ('attachment_url', 'attachment_name', 'attachment_size')
        }),
        ('Status', {
            'fields': ('is_read', 'read_at')
        }),
        ('Reply', {
            'fields': ('reply_to',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def content_preview(self, obj):
        if obj.content:
            return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
        return '-'
    content_preview.short_description = 'Content'
    
    def attachment_info(self, obj):
        if obj.attachment_url:
            return f"{obj.attachment_name} ({obj.attachment_size} bytes)" if obj.attachment_size else obj.attachment_name
        return 'No attachment'
    attachment_info.short_description = 'Attachment'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('sender', 'chat_room', 'reply_to')


@admin.register(ChatParticipant)
class ChatParticipantAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'chat_room', 'user', 'is_online', 'last_seen', 'unread_count',
        'notifications_enabled', 'created_at'
    ]
    list_filter = ['is_online', 'notifications_enabled', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'chat_room__title']
    ordering = ['-created_at']
    list_editable = ['is_online', 'notifications_enabled']
    raw_id_fields = ['chat_room', 'user']
    
    fieldsets = (
        ('Participant Information', {
            'fields': ('chat_room', 'user')
        }),
        ('Status', {
            'fields': ('is_online', 'last_seen', 'unread_count')
        }),
        ('Notifications', {
            'fields': ('notifications_enabled', 'mute_until')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'chat_room')


@admin.register(ChatTemplate)
class ChatTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'name', 'category', 'subject_preview', 'is_active', 'usage_count', 'created_at'
    ]
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'subject', 'content']
    ordering = ['category', 'name']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Template Information', {
            'fields': ('name', 'category', 'is_active')
        }),
        ('Content', {
            'fields': ('subject', 'content')
        }),
        ('Variables', {
            'fields': ('variables',)
        }),
        ('Usage', {
            'fields': ('usage_count',)
        }),
    )
    
    def subject_preview(self, obj):
        if obj.subject:
            return obj.subject[:50] + '...' if len(obj.subject) > 50 else obj.subject
        return '-'
    subject_preview.short_description = 'Subject'


@admin.register(ChatNotification)
class ChatNotificationAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'chat_room', 'notification_type', 'is_read', 'created_at'
    ]
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__first_name', 'chat_room__name']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Notification Information', {
            'fields': ('user', 'chat_room', 'message', 'notification_type')
        }),
        ('Status', {
            'fields': ('is_read', 'read_at')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'chat_room', 'message')


@admin.register(ChatReport)
class ChatReportAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'reported_by', 'reported_message', 'reason', 'status', 'created_at'
    ]
    list_filter = ['reason', 'status', 'created_at']
    search_fields = ['reported_by__first_name', 'reported_message__content', 'description']
    ordering = ['-created_at']
    list_editable = ['status']
    
    fieldsets = (
        ('Report Information', {
            'fields': ('reported_message', 'reported_by', 'reason', 'description', 'evidence')
        }),
        ('Status', {
            'fields': ('status', 'admin_notes')
        }),
        ('Resolution', {
            'fields': ('resolved_by', 'resolved_at', 'action_taken')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('reported_by', 'reported_message', 'resolved_by')

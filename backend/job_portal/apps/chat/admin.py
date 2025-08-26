from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Max, Q
from .models import ChatRoom, ChatMessage, ChatParticipant, ChatTemplate, ChatNotification, ChatReport


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'name', 'room_type', 'order', 'participants_count', 'messages_count',
        'last_message_time', 'created_at'
    ]
    list_filter = ['room_type', 'created_at']
    search_fields = ['name', 'order__title']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Room Information', {
            'fields': ('name', 'room_type', 'order')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def participants_count(self, obj):
        return obj.participants.filter(is_active=True).count()
    participants_count.short_description = 'Participants'
    
    def messages_count(self, obj):
        return obj.messages.count()
    messages_count.short_description = 'Messages'
    
    def last_message_time(self, obj):
        last_msg = obj.messages.order_by('-created_at').first()
        return last_msg.created_at if last_msg else '-'
    last_message_time.short_description = 'Last Message'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order').annotate(
            participants_count=Count('participants', filter=Q(participants__is_active=True)),
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
        'id', 'chat_room', 'user', 'role', 'is_active', 'joined_at',
        'last_read_at', 'days_since_last_read'
    ]
    list_filter = ['role', 'is_active', 'joined_at']
    search_fields = ['user__first_name', 'user__last_name', 'chat_room__name']
    ordering = ['-joined_at']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Participant Information', {
            'fields': ('chat_room', 'user', 'role')
        }),
        ('Status', {
            'fields': ('is_active', 'joined_at', 'last_read_at')
        }),
    )
    
    def days_since_last_read(self, obj):
        if obj.last_read_at:
            from django.utils import timezone
            delta = timezone.now() - obj.last_read_at
            return delta.days
        return '-'
    days_since_last_read.short_description = 'Days Since Last Read'
    
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
        'id', 'reporter', 'chat_room', 'report_type', 'status', 'created_at'
    ]
    list_filter = ['report_type', 'status', 'created_at']
    search_fields = ['reporter__first_name', 'chat_room__name', 'description']
    ordering = ['-created_at']
    list_editable = ['status']
    
    fieldsets = (
        ('Report Information', {
            'fields': ('reporter', 'chat_room', 'report_type', 'description')
        }),
        ('Status', {
            'fields': ('status', 'admin_notes')
        }),
        ('Resolution', {
            'fields': ('resolved_by', 'resolved_at', 'resolution')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('reporter', 'chat_room', 'resolved_by')

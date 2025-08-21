from django.db import models
from django.utils.translation import gettext_lazy as _
from utils.abstract_models import AbstractSoftDeleteModel, AbstractTimestampedModel
from accounts.models import UserModel


class ChatRoom(AbstractSoftDeleteModel, AbstractTimestampedModel):
    """Chat room for communication between users."""
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='chat_rooms')
    participants = models.ManyToManyField(UserModel, related_name='chat_rooms')
    
    # Chat room details
    title = models.CharField(_("Chat Title"), max_length=200, blank=True)
    is_active = models.BooleanField(_("Active"), default=True)
    last_message_at = models.DateTimeField(_("Last Message At"), null=True, blank=True)
    
    # Chat room type
    chat_type = models.CharField(_("Chat Type"), max_length=20, choices=[
        ('order_chat', _('Order Chat')),
        ('support_chat', _('Support Chat')),
        ('general_chat', _('General Chat')),
    ], default='order_chat')
    
    class Meta:
        verbose_name = _("Chat Room")
        verbose_name_plural = _("Chat Rooms")
        ordering = ['-last_message_at', '-created_at']
    
    def __str__(self):
        return f"Chat Room #{self.id} - {self.title or self.order.title} [#{self.id}]"


class ChatMessage(AbstractSoftDeleteModel, AbstractTimestampedModel):
    """Individual chat messages."""
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='sent_messages')
    
    # Message content
    message_type = models.CharField(_("Message Type"), max_length=20, choices=[
        ('text', _('Text')),
        ('image', _('Image')),
        ('file', _('File')),
        ('system', _('System Message')),
        ('order_update', _('Order Update')),
    ], default='text')
    
    content = models.TextField(_("Message Content"))
    attachment_url = models.URLField(_("Attachment URL"), blank=True)
    attachment_name = models.CharField(_("Attachment Name"), max_length=200, blank=True)
    attachment_size = models.PositiveIntegerField(_("Attachment Size (bytes)"), null=True, blank=True)
    
    # Message status
    is_read = models.BooleanField(_("Read"), default=False)
    read_at = models.DateTimeField(_("Read At"), null=True, blank=True)
    
    # Reply functionality
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    
    class Meta:
        verbose_name = _("Chat Message")
        verbose_name_plural = _("Chat Messages")
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender.name}: {self.content[:50]}... [#{self.id}]"


class ChatParticipant(AbstractTimestampedModel):
    """Track participant status in chat rooms."""
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='participant_status')
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='chat_participant_status')
    
    # Participant status
    is_online = models.BooleanField(_("Online"), default=False)
    last_seen = models.DateTimeField(_("Last Seen"), null=True, blank=True)
    unread_count = models.PositiveIntegerField(_("Unread Messages"), default=0)
    
    # Notification preferences
    notifications_enabled = models.BooleanField(_("Notifications Enabled"), default=True)
    mute_until = models.DateTimeField(_("Mute Until"), null=True, blank=True)
    
    class Meta:
        verbose_name = _("Chat Participant")
        verbose_name_plural = _("Chat Participants")
        unique_together = ['chat_room', 'user']
    
    def __str__(self):
        return f"{self.user.name} in {self.chat_room.title} [#{self.id}]"


class ChatTemplate(AbstractSoftDeleteModel, AbstractTimestampedModel):
    """Predefined chat message templates."""
    name = models.CharField(_("Template Name"), max_length=100)
    category = models.CharField(_("Category"), max_length=50, choices=[
        ('greeting', _('Greeting')),
        ('order_update', _('Order Update')),
        ('support', _('Support')),
        ('general', _('General')),
    ])
    
    # Template content
    subject = models.CharField(_("Subject"), max_length=200, blank=True)
    content = models.TextField(_("Template Content"))
    variables = models.JSONField(_("Template Variables"), default=list)  # List of available variables
    
    # Usage
    is_active = models.BooleanField(_("Active"), default=True)
    usage_count = models.PositiveIntegerField(_("Usage Count"), default=0)
    
    class Meta:
        verbose_name = _("Chat Template")
        verbose_name_plural = _("Chat Templates")
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.get_category_display()} - {self.name} [#{self.id}]"


class ChatNotification(AbstractTimestampedModel):
    """Chat notifications for users."""
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='chat_notifications')
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='notifications')
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='notifications')
    
    # Notification details
    notification_type = models.CharField(_("Notification Type"), max_length=20, choices=[
        ('new_message', _('New Message')),
        ('mention', _('Mention')),
        ('order_update', _('Order Update')),
        ('system', _('System Notification')),
    ])
    
    # Status
    is_read = models.BooleanField(_("Read"), default=False)
    read_at = models.DateTimeField(_("Read At"), null=True, blank=True)
    
    # Delivery
    sent_via = models.CharField(_("Sent Via"), max_length=20, choices=[
        ('push', _('Push Notification')),
        ('email', _('Email')),
        ('sms', _('SMS')),
        ('in_app', _('In-App')),
    ], default='in_app')
    
    class Meta:
        verbose_name = _("Chat Notification")
        verbose_name_plural = _("Chat Notifications")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.name} - {self.get_notification_type_display()} [#{self.id}]"


class ChatReport(AbstractTimestampedModel):
    """Reports of inappropriate chat content."""
    reported_message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='reports')
    reported_by = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='chat_reports_filed')
    
    # Report details
    reason = models.CharField(_("Report Reason"), max_length=50, choices=[
        ('spam', _('Spam')),
        ('harassment', _('Harassment')),
        ('inappropriate_content', _('Inappropriate Content')),
        ('fake_information', _('Fake Information')),
        ('other', _('Other')),
    ])
    description = models.TextField(_("Report Description"))
    evidence = models.JSONField(_("Evidence"), default=list)  # List of file URLs
    
    # Status
    status = models.CharField(_("Status"), max_length=20, choices=[
        ('pending', _('Pending')),
        ('under_review', _('Under Review')),
        ('resolved', _('Resolved')),
        ('dismissed', _('Dismissed')),
    ], default='pending')
    
    # Admin handling
    admin_notes = models.TextField(_("Admin Notes"), blank=True)
    resolved_by = models.ForeignKey(UserModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='chat_reports_resolved')
    resolved_at = models.DateTimeField(_("Resolved At"), null=True, blank=True)
    action_taken = models.TextField(_("Action Taken"), blank=True)
    
    class Meta:
        verbose_name = _("Chat Report")
        verbose_name_plural = _("Chat Reports")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Report on message from {self.reported_message.sender.name} - {self.get_reason_display()} [#{self.id}]"

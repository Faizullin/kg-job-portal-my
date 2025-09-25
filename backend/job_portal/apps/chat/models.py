from django.db import models
from django.utils.translation import gettext_lazy as _
from utils.abstract_models import AbstractSoftDeleteModel, AbstractTimestampedModel
from accounts.models import UserModel


class ChatType(models.TextChoices):
    ORDER_CHAT = 'order_chat', _('Order Chat')
    SUPPORT_CHAT = 'support_chat', _('Support Chat')
    GENERAL_CHAT = 'general_chat', _('General Chat')


class MessageType(models.TextChoices):
    TEXT = 'text', _('Text')
    IMAGE = 'image', _('Image')
    FILE = 'file', _('File')
    SYSTEM = 'system', _('System Message')
    ORDER_UPDATE = 'order_update', _('Order Update')


class ChatRole(models.TextChoices):
    MEMBER = 'member', _('Member')
    ADMIN = 'admin', _('Admin')
    MODERATOR = 'moderator', _('Moderator')


class ChatRoom(AbstractSoftDeleteModel, AbstractTimestampedModel):
    """Chat room for communication between users."""
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='chat_rooms', null=True, blank=True)
    participants = models.ManyToManyField(UserModel, through='ChatParticipant', related_name='chat_rooms')
    
    # Chat room details
    title = models.CharField(_("Chat Title"), max_length=200, blank=True)
    is_active = models.BooleanField(_("Active"), default=True)
    last_message_at = models.DateTimeField(_("Last Message At"), null=True, blank=True)
    
    # Chat room type
    chat_type = models.CharField(_("Chat Type"), max_length=20, choices=ChatType.choices, default=ChatType.ORDER_CHAT)
    
    class Meta:
        verbose_name = _("Chat Room")
        verbose_name_plural = _("Chat Rooms")
        ordering = ['-last_message_at', '-created_at']
    
    def __str__(self):
        return f"Chat Room #{self.id} - {self.title} [#{self.id}]"


class ChatMessage(AbstractSoftDeleteModel, AbstractTimestampedModel):
    """Individual chat messages."""
    # Uses default SoftDeleteManager from AbstractSoftDeleteModel
    
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='sent_messages')
    
    # Message content
    message_type = models.CharField(_("Message Type"), max_length=20, choices=MessageType.choices, default=MessageType.TEXT)
    
    content = models.TextField(_("Message Content"))
    
    # File attachments (changed from URL to actual file upload)
    attachment = models.FileField(_("Attachment"), upload_to='chat_attachments/', blank=True)
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
        sender_name = f"{self.sender.first_name} {self.sender.last_name}".strip() or self.sender.username
        return f"{sender_name}: {self.content[:50]}... [#{self.id}]"


class ChatParticipant(AbstractTimestampedModel):
    """Track participant status in chat rooms."""
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='participant_status')
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='chat_participant_status')
    
    # Participant role
    role = models.CharField(_("Role"), max_length=20, choices=ChatRole.choices, default=ChatRole.MEMBER)
    
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
        user_name = f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username
        room_title = self.chat_room.title or (self.chat_room.order.title if self.chat_room.order else 'General Chat')
        return f"{user_name} in {room_title} [#{self.id}]"





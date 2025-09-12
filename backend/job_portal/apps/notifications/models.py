from django.db import models
from django.utils.translation import gettext_lazy as _
from utils.abstract_models import AbstractSoftDeleteModel, AbstractTimestampedModel
from accounts.models import UserModel


class NotificationTemplate(AbstractSoftDeleteModel, AbstractTimestampedModel):
    """Templates for different types of notifications."""
    name = models.CharField(_("Template Name"), max_length=100)
    notification_type = models.CharField(_("Notification Type"), max_length=50, choices=[
        ('order_update', _('Order Update')),
        ('bid_received', _('Bid Received')),
        ('payment_success', _('Payment Success')),
        ('payment_failed', _('Payment Failed')),
        ('chat_message', _('Chat Message')),
        ('system_alert', _('System Alert')),
        ('promotional', _('Promotional')),
    ])
    
    # Content
    subject = models.CharField(_("Subject"), max_length=200)
    message = models.TextField(_("Message Content"))
    short_message = models.CharField(_("Short Message"), max_length=160, blank=True)  # For SMS
    
    # Channels
    email_enabled = models.BooleanField(_("Email Enabled"), default=True)
    push_enabled = models.BooleanField(_("Push Enabled"), default=True)
    sms_enabled = models.BooleanField(_("SMS Enabled"), default=False)
    in_app_enabled = models.BooleanField(_("In-App Enabled"), default=True)
    
    # Variables
    variables = models.JSONField(_("Template Variables"), default=list)  # List of available variables
    
    # Status
    is_active = models.BooleanField(_("Active"), default=True)
    
    class Meta:
        verbose_name = _("Notification Template")
        verbose_name_plural = _("Notification Templates")
        ordering = ['notification_type', 'name']
    
    def __str__(self):
        return f"{self.name}... [#{self.id}]"


class UserNotification(AbstractSoftDeleteModel, AbstractTimestampedModel):
    """Individual notifications sent to users."""
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='notifications')
    template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE, related_name='notifications')
    
    # Notification content
    subject = models.CharField(_("Subject"), max_length=200)
    message = models.TextField(_("Message Content"))
    short_message = models.CharField(_("Short Message"), max_length=160, blank=True)
    
    # Context
    context_data = models.JSONField(_("Context Data"), default=dict)  # Additional data for the notification
    related_object_type = models.CharField(_("Related Object Type"), max_length=50, blank=True)
    related_object_id = models.PositiveIntegerField(_("Related Object ID"), null=True, blank=True)
    
    # Status
    status = models.CharField(_("Status"), max_length=20, choices=[
        ('pending', _('Pending')),
        ('sent', _('Sent')),
        ('delivered', _('Delivered')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled')),
    ], default='pending')
    
    # Delivery tracking
    sent_at = models.DateTimeField(_("Sent At"), null=True, blank=True)
    delivered_at = models.DateTimeField(_("Delivered At"), null=True, blank=True)
    failed_at = models.DateTimeField(_("Failed At"), null=True, blank=True)
    
    # Read status
    is_read = models.BooleanField(_("Read"), default=False)
    read_at = models.DateTimeField(_("Read At"), null=True, blank=True)
    
    # Priority
    priority = models.CharField(_("Priority"), max_length=20, choices=[
        ('low', _('Low')),
        ('normal', _('Normal')),
        ('high', _('High')),
        ('urgent', _('Urgent')),
    ], default='normal')
    
    class Meta:
        verbose_name = _("User Notification")
        verbose_name_plural = _("User Notifications")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.name} - {self.subject}... [#{self.id}]"


class NotificationDelivery(AbstractTimestampedModel):
    """Track delivery of notifications across different channels."""
    notification = models.ForeignKey(UserNotification, on_delete=models.CASCADE, related_name='deliveries')
    
    # Delivery details
    channel = models.CharField(_("Channel"), max_length=20, choices=[
        ('email', _('Email')),
        ('push', _('Push Notification')),
        ('sms', _('SMS')),
        ('in_app', _('In-App')),
    ])
    
    # Status
    status = models.CharField(_("Status"), max_length=20, choices=[
        ('pending', _('Pending')),
        ('sent', _('Sent')),
        ('delivered', _('Delivered')),
        ('failed', _('Failed')),
        ('bounced', _('Bounced')),
    ], default='pending')
    
    # Delivery tracking
    sent_at = models.DateTimeField(_("Sent At"), null=True, blank=True)
    delivered_at = models.DateTimeField(_("Delivered At"), null=True, blank=True)
    failed_at = models.DateTimeField(_("Failed At"), null=True, blank=True)
    
    # Error handling
    error_message = models.TextField(_("Error Message"), blank=True)
    retry_count = models.PositiveIntegerField(_("Retry Count"), default=0)
    
    # External service response
    external_id = models.CharField(_("External ID"), max_length=100, blank=True)
    external_response = models.JSONField(_("External Response"), default=dict)
    
    class Meta:
        verbose_name = _("Notification Delivery")
        verbose_name_plural = _("Notification Deliveries")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification.subject} via {self.get_channel_display()}... [#{self.id}]"


class NotificationPreference(AbstractTimestampedModel):
    """User preferences for notifications."""
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # General preferences
    email_notifications = models.BooleanField(_("Email Notifications"), default=True)
    push_notifications = models.BooleanField(_("Push Notifications"), default=True)
    sms_notifications = models.BooleanField(_("SMS Notifications"), default=False)
    in_app_notifications = models.BooleanField(_("In-App Notifications"), default=True)
    
    # Specific notification types
    order_updates = models.BooleanField(_("Order Updates"), default=True)
    bid_notifications = models.BooleanField(_("Bid Notifications"), default=True)
    payment_notifications = models.BooleanField(_("Payment Notifications"), default=True)
    chat_notifications = models.BooleanField(_("Chat Notifications"), default=True)
    promotional_notifications = models.BooleanField(_("Promotional Notifications"), default=False)
    system_notifications = models.BooleanField(_("System Notifications"), default=True)
    
    # Timing preferences
    quiet_hours_start = models.TimeField(_("Quiet Hours Start"), null=True, blank=True)
    quiet_hours_end = models.TimeField(_("Quiet Hours End"), null=True, blank=True)
    timezone = models.CharField(_("Timezone"), max_length=50, default='UTC')
    
    # Frequency
    digest_frequency = models.CharField(_("Digest Frequency"), max_length=20, choices=[
        ('immediate', _('Immediate')),
        ('hourly', _('Hourly')),
        ('daily', _('Daily')),
        ('weekly', _('Weekly')),
    ], default='immediate')
    
    class Meta:
        verbose_name = _("Notification Preference")
        verbose_name_plural = _("Notification Preferences")
    
    def __str__(self):
        return f"{self.user.name} - Notification Preferences... [#{self.id}]"


class NotificationQueue(AbstractTimestampedModel):
    """Queue for processing notifications asynchronously."""
    notification = models.ForeignKey(UserNotification, on_delete=models.CASCADE, related_name='queue_entries')
    
    # Queue details
    priority = models.PositiveIntegerField(_("Priority"), default=0)  # Lower number = higher priority
    scheduled_at = models.DateTimeField(_("Scheduled At"), null=True, blank=True)
    retry_count = models.PositiveIntegerField(_("Retry Count"), default=0)
    max_retries = models.PositiveIntegerField(_("Max Retries"), default=3)
    
    # Status
    status = models.CharField(_("Status"), max_length=20, choices=[
        ('queued', _('Queued')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled')),
    ], default='queued')
    
    # Processing
    started_at = models.DateTimeField(_("Started At"), null=True, blank=True)
    completed_at = models.DateTimeField(_("Completed At"), null=True, blank=True)
    
    class Meta:
        verbose_name = _("Notification Queue")
        verbose_name_plural = _("Notification Queue")
        ordering = ['priority', 'scheduled_at', 'created_at']
    
    def __str__(self):
        return f"Queue Entry #{self.id} - {self.notification.subject}... [#{self.id}]"

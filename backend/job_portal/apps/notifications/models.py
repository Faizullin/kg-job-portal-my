from django.db import models
from django.utils.translation import gettext_lazy as _
from utils.abstract_models import AbstractTimestampedModel
from accounts.models import UserModel


class NotificationType(models.TextChoices):
    BID_RECEIVED = 'bid_received', _('Bid Received')
    BID_ACCEPTED = 'bid_accepted', _('Bid Accepted')
    BID_REJECTED = 'bid_rejected', _('Bid Rejected')
    ORDER_ASSIGNED = 'order_assigned', _('Order Assigned')
    ORDER_COMPLETED = 'order_completed', _('Order Completed')
    CHAT_MESSAGE = 'chat_message', _('Chat Message')
    SYSTEM_ALERT = 'system_alert', _('System Alert')


class UserNotification(AbstractTimestampedModel):
    """Individual notifications sent to users for important events."""
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='notifications')
    
    # Content
    title = models.CharField(_("Title"), max_length=200)
    message = models.TextField(_("Message Content"))
    
    # Notification type for important events only
    notification_type = models.CharField(_("Notification Type"), max_length=50, choices=NotificationType.choices)
    
    # Status
    is_read = models.BooleanField(_("Read"), default=False)
    read_at = models.DateTimeField(_("Read At"), null=True, blank=True)
    
    # Related objects for context
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    bid = models.ForeignKey('orders.Bid', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    
    class Meta:
        verbose_name = _("User Notification")
        verbose_name_plural = _("User Notifications")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}... [#{self.id}]"
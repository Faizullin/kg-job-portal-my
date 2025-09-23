from django.db import models
from django.utils.translation import gettext_lazy as _
from utils.abstract_models import AbstractTimestampedModel
from accounts.models import UserModel


class UserNotification(AbstractTimestampedModel):
    """Individual notifications sent to users for important events."""
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='notifications')
    
    # Content
    title = models.CharField(_("Title"), max_length=200)
    message = models.TextField(_("Message Content"))
    
    # Notification type for important events only
    notification_type = models.CharField(_("Notification Type"), max_length=50, choices=[
        ('bid_received', _('Bid Received')),
        ('bid_accepted', _('Bid Accepted')),
        ('bid_rejected', _('Bid Rejected')),
        ('order_assigned', _('Order Assigned')),
        ('order_completed', _('Order Completed')),
        ('chat_message', _('Chat Message')),
        ('system_alert', _('System Alert')),
    ])
    
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
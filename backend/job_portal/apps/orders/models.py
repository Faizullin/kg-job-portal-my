# Django imports
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

# Local imports
from utils.abstract_models import AbstractSoftDeleteModel, AbstractTimestampedModel, AbstractCascadingSoftDeleteModel
from accounts.models import UserModel
from job_portal.apps.chat.models import ChatRoom, ChatParticipant


class OrderUrgency(models.TextChoices):
    LOW = 'low', _('Low')
    MEDIUM = 'medium', _('Medium')
    HIGH = 'high', _('High')
    URGENT = 'urgent', _('Urgent')


class OrderStatus(models.TextChoices):
    DRAFT = 'draft', _('Draft')
    PUBLISHED = 'published', _('Published')
    BIDDING = 'bidding', _('Bidding')
    ASSIGNED = 'assigned', _('Assigned')
    IN_PROGRESS = 'in_progress', _('In Progress')
    COMPLETED = 'completed', _('Completed')
    CANCELLED = 'cancelled', _('Cancelled')
    DISPUTED = 'disputed', _('Disputed')


class BidStatus(models.TextChoices):
    PENDING = 'pending', _('Pending')
    ACCEPTED = 'accepted', _('Accepted')
    REJECTED = 'rejected', _('Rejected')
    WITHDRAWN = 'withdrawn', _('Withdrawn')


class DisputeType(models.TextChoices):
    QUALITY_ISSUE = 'quality_issue', _('Quality Issue')
    PAYMENT_DISPUTE = 'payment_dispute', _('Payment Dispute')
    SCHEDULE_CONFLICT = 'schedule_conflict', _('Schedule Conflict')
    COMMUNICATION_ISSUE = 'communication_issue', _('Communication Issue')
    OTHER = 'other', _('Other')


class DisputeStatus(models.TextChoices):
    OPEN = 'open', _('Open')
    UNDER_REVIEW = 'under_review', _('Under Review')
    RESOLVED = 'resolved', _('Resolved')
    CLOSED = 'closed', _('Closed')


class Order(AbstractCascadingSoftDeleteModel, AbstractTimestampedModel):
    """Main order model for service requests."""
    client = models.ForeignKey('users.ClientProfile', on_delete=models.CASCADE, related_name='orders')
    service_subcategory = models.ForeignKey('core.ServiceSubcategory', on_delete=models.CASCADE, related_name='orders')
    
    # Order details
    title = models.CharField(_("Order Title"), max_length=200)
    description = models.TextField(_("Order Description"))
    location = models.TextField(_("Service Location"))
    city = models.CharField(_("City"), max_length=100)
    state = models.CharField(_("State/Province"), max_length=100)
    country = models.CharField(_("Country"), max_length=100)
    postal_code = models.CharField(_("Postal Code"), max_length=20)
    
    # Service requirements
    service_date = models.DateField(_("Preferred Service Date"), null=True, blank=True)
    service_time = models.TimeField(_("Preferred Service Time"), null=True, blank=True)
    urgency = models.CharField(_("Urgency"), max_length=20, choices=OrderUrgency.choices, default=OrderUrgency.MEDIUM)
    
    # Budget and pricing
    budget_min = models.DecimalField(_("Minimum Budget"), max_digits=10, decimal_places=2, null=True, blank=True)
    budget_max = models.DecimalField(_("Maximum Budget"), max_digits=10, decimal_places=2, null=True, blank=True)
    final_price = models.DecimalField(_("Final Price"), max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Order status
    status = models.CharField(_("Order Status"), max_length=20, choices=OrderStatus.choices, default=OrderStatus.DRAFT)
    
    # Timestamps
    published_at = models.DateTimeField(_("Published At"), null=True, blank=True)
    assigned_at = models.DateTimeField(_("Assigned At"), null=True, blank=True)
    started_at = models.DateTimeField(_("Started At"), null=True, blank=True)
    completed_at = models.DateTimeField(_("Completed At"), null=True, blank=True)
    cancelled_at = models.DateTimeField(_("Cancelled At"), null=True, blank=True)
    
    # Additional information
    attachments = models.ManyToManyField('OrderAttachment', blank=True, related_name='orders')
    special_requirements = models.TextField(_("Special Requirements"), blank=True)
    is_featured = models.BooleanField(_("Featured Order"), default=False)
    
    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")
        ordering = ['-created_at']
    
    def get_cascade_fields(self):
        """Specify fields that should cascade soft delete."""
        return ['bids']
    
    def save(self, *args, **kwargs):
        """Override save to auto-create chat room when order is published."""
        is_new = self.pk is None
        was_published = False
        
        if not is_new:
            try:
                old_order = Order.objects.get(pk=self.pk)
                was_published = old_order.status == 'published'
            except Order.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        # Auto-create chat room when order is published
        if not was_published and self.status == 'published' and not is_new:
            self._create_chat_room()
    
    def _create_chat_room(self):
        """Create chat room for this order."""
        # Create chat room
        chat_room = ChatRoom.objects.create(
            order=self,
            title=f"Chat for Order: {self.title}",
            chat_type='order_chat'
        )
        
        # Add client as participant
        ChatParticipant.objects.create(
            chat_room=chat_room,
            user=self.client.user_profile.user,
            role='member'
        )
        
        return chat_room
    
    def add_provider_to_chat(self, provider):
        """Add service provider to the order's chat room."""
        if not self.chat_rooms.exists():
            self._create_chat_room()
        
        chat_room = self.chat_rooms.first()
        
        # Check if provider is already in the chat
        if not chat_room.participants.filter(id=provider.user_profile.user.id).exists():
            ChatParticipant.objects.create(
                chat_room=chat_room,
                user=provider.user_profile.user,
                role='member'
            )
        
        return chat_room
    
    def __str__(self):
        return f"Order #{self.id} - {self.title} [#{self.id}]"




class Bid(AbstractSoftDeleteModel, AbstractTimestampedModel):
    """Bids from service providers on orders."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='bids')
    provider = models.ForeignKey('users.ServiceProviderProfile', on_delete=models.CASCADE, related_name='bids')
    
    # Bid details
    amount = models.DecimalField(_("Bid Amount"), max_digits=10, decimal_places=2)
    description = models.TextField(_("Bid Description"))
    estimated_duration = models.PositiveIntegerField(_("Estimated Duration (hours)"), null=True, blank=True)
    
    # Bid status
    status = models.CharField(_("Bid Status"), max_length=20, choices=BidStatus.choices, default=BidStatus.PENDING)
    
    # Timestamps
    accepted_at = models.DateTimeField(_("Accepted At"), null=True, blank=True)
    rejected_at = models.DateTimeField(_("Rejected At"), null=True, blank=True)
    withdrawn_at = models.DateTimeField(_("Withdrawn At"), null=True, blank=True)
    
    # Additional information
    terms_conditions = models.TextField(_("Terms & Conditions"), blank=True)
    is_negotiable = models.BooleanField(_("Price Negotiable"), default=False)
    
    class Meta:
        verbose_name = _("Bid")
        verbose_name_plural = _("Bids")
        ordering = ['amount', '-created_at']
        unique_together = ['order', 'provider']
    
    def __str__(self):
        return f"{self.provider.user_profile.user.username} - ${self.amount} on {self.order.title} [#{self.id}]"


class OrderAssignment(AbstractTimestampedModel):
    """Assignment of orders to service providers."""
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='assignment')
    provider = models.ForeignKey('users.ServiceProviderProfile', on_delete=models.CASCADE, related_name='assignments')
    accepted_bid = models.ForeignKey(Bid, on_delete=models.CASCADE, related_name='assignment')
    
    # Assignment details
    assigned_at = models.DateTimeField(_("Assigned At"), auto_now_add=True)
    start_date = models.DateField(_("Start Date"), null=True, blank=True)
    start_time = models.TimeField(_("Start Time"), null=True, blank=True)
    
    # Progress tracking
    progress_notes = models.TextField(_("Progress Notes"), blank=True)
    completion_notes = models.TextField(_("Completion Notes"), blank=True)
    
    # Client feedback
    client_rating = models.PositiveIntegerField(_("Client Rating"), null=True, blank=True, 
                                             validators=[MinValueValidator(1), MaxValueValidator(5)])
    client_review = models.TextField(_("Client Review"), blank=True)
    
    class Meta:
        verbose_name = _("Order Assignment")
        verbose_name_plural = _("Order Assignments")
    
    def __str__(self):
        return f"{self.order.title} - {self.provider.user_profile.user.username} [#{self.id}]"


class OrderDispute(AbstractTimestampedModel):
    """Disputes related to orders."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='disputes')
    raised_by = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='disputes_raised')
    
    # Dispute details
    dispute_type = models.CharField(_("Dispute Type"), max_length=50, choices=DisputeType.choices)
    description = models.TextField(_("Dispute Description"))
    evidence = models.JSONField(_("Evidence"), default=list)  # List of file URLs
    
    # Resolution
    status = models.CharField(_("Status"), max_length=20, choices=DisputeStatus.choices, default=DisputeStatus.OPEN)
    
    # Admin handling
    admin_notes = models.TextField(_("Admin Notes"), blank=True)
    resolved_by = models.ForeignKey(UserModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='disputes_resolved')
    resolved_at = models.DateTimeField(_("Resolved At"), null=True, blank=True)
    resolution = models.TextField(_("Resolution"), blank=True)
    
    class Meta:
        verbose_name = _("Order Dispute")
        verbose_name_plural = _("Order Disputes")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Dispute on {self.order.title} - {self.get_dispute_type_display()} [#{self.id}]"


class OrderAttachment(AbstractTimestampedModel):
    file_name = models.CharField(_("File Name"), max_length=255)
    file_type = models.CharField(_("File Type"), max_length=50)
    file_size = models.PositiveIntegerField(_("File Size (bytes)"))
    file_url = models.URLField(_("File URL"))
    mime_type = models.CharField(_("MIME Type"), max_length=100, blank=True)
    description = models.TextField(_("Description"), blank=True)
    uploaded_by = models.ForeignKey('accounts.UserModel', on_delete=models.CASCADE, related_name='uploaded_attachments')
    
    class Meta:
        verbose_name = _("Order Attachment")
        verbose_name_plural = _("Order Attachments")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.file_name}... [#{self.id}]"

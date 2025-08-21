from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from utils.abstract_models import AbstractSoftDeleteModel, AbstractTimestampedModel, AbstractCascadingSoftDeleteModel
from accounts.models import UserModel


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
    urgency = models.CharField(_("Urgency"), max_length=20, choices=[
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('urgent', _('Urgent')),
    ], default='medium')
    
    # Budget and pricing
    budget_min = models.DecimalField(_("Minimum Budget"), max_digits=10, decimal_places=2, null=True, blank=True)
    budget_max = models.DecimalField(_("Maximum Budget"), max_digits=10, decimal_places=2, null=True, blank=True)
    final_price = models.DecimalField(_("Final Price"), max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Order status
    status = models.CharField(_("Order Status"), max_length=20, choices=[
        ('draft', _('Draft')),
        ('published', _('Published')),
        ('bidding', _('Bidding')),
        ('assigned', _('Assigned')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
        ('disputed', _('Disputed')),
    ], default='draft')
    
    # Timestamps
    published_at = models.DateTimeField(_("Published At"), null=True, blank=True)
    assigned_at = models.DateTimeField(_("Assigned At"), null=True, blank=True)
    started_at = models.DateTimeField(_("Started At"), null=True, blank=True)
    completed_at = models.DateTimeField(_("Completed At"), null=True, blank=True)
    cancelled_at = models.DateTimeField(_("Cancelled At"), null=True, blank=True)
    
    # Additional information
    attachments = models.JSONField(_("Attachments"), default=list)  # List of file URLs
    special_requirements = models.TextField(_("Special Requirements"), blank=True)
    is_featured = models.BooleanField(_("Featured Order"), default=False)
    
    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")
        ordering = ['-created_at']
    
    def get_cascade_fields(self):
        """Specify fields that should cascade soft delete."""
        return ['bids', 'order_addons', 'order_photos']
    
    def __str__(self):
        return f"Order #{self.id} - {self.title} [#{self.id}]"


class OrderAddon(AbstractSoftDeleteModel, AbstractTimestampedModel):
    """Add-ons selected for an order."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_addons')
    addon = models.ForeignKey('core.ServiceAddon', on_delete=models.CASCADE, related_name='order_addons')
    quantity = models.PositiveIntegerField(_("Quantity"), default=1)
    price = models.DecimalField(_("Price"), max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = _("Order Addon")
        verbose_name_plural = _("Order Addons")
        unique_together = ['order', 'addon']
    
    def __str__(self):
        return f"{self.order.title} - {self.addon.name} [#{self.id}]"


class OrderPhoto(AbstractSoftDeleteModel, AbstractTimestampedModel):
    """Photos attached to orders."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_photos')
    photo_url = models.URLField(_("Photo URL"))
    caption = models.CharField(_("Caption"), max_length=200, blank=True)
    is_primary = models.BooleanField(_("Primary Photo"), default=False)
    
    class Meta:
        verbose_name = _("Order Photo")
        verbose_name_plural = _("Order Photos")
        ordering = ['-is_primary', '-created_at']
    
    def __str__(self):
        return f"{self.order.title} - Photo [#{self.id}]"


class Bid(AbstractSoftDeleteModel, AbstractTimestampedModel):
    """Bids from service providers on orders."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='bids')
    provider = models.ForeignKey('users.ServiceProviderProfile', on_delete=models.CASCADE, related_name='bids')
    
    # Bid details
    amount = models.DecimalField(_("Bid Amount"), max_digits=10, decimal_places=2)
    description = models.TextField(_("Bid Description"))
    estimated_duration = models.PositiveIntegerField(_("Estimated Duration (hours)"), null=True, blank=True)
    
    # Bid status
    status = models.CharField(_("Bid Status"), max_length=20, choices=[
        ('pending', _('Pending')),
        ('accepted', _('Accepted')),
        ('rejected', _('Rejected')),
        ('withdrawn', _('Withdrawn')),
    ], default='pending')
    
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
        return f"{self.provider.user_profile.user.name} - ${self.amount} on {self.order.title} [#{self.id}]"


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
        return f"{self.order.title} - {self.provider.user_profile.user.name} [#{self.id}]"


class OrderDispute(AbstractTimestampedModel):
    """Disputes related to orders."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='disputes')
    raised_by = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='disputes_raised')
    
    # Dispute details
    dispute_type = models.CharField(_("Dispute Type"), max_length=50, choices=[
        ('quality_issue', _('Quality Issue')),
        ('payment_dispute', _('Payment Dispute')),
        ('schedule_conflict', _('Schedule Conflict')),
        ('communication_issue', _('Communication Issue')),
        ('other', _('Other')),
    ])
    description = models.TextField(_("Dispute Description"))
    evidence = models.JSONField(_("Evidence"), default=list)  # List of file URLs
    
    # Resolution
    status = models.CharField(_("Status"), max_length=20, choices=[
        ('open', _('Open')),
        ('under_review', _('Under Review')),
        ('resolved', _('Resolved')),
        ('closed', _('Closed')),
    ], default='open')
    
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

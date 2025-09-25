from django.db import models
from django.utils.translation import gettext_lazy as _
from utils.abstract_models import AbstractSoftDeleteModel, AbstractTimestampedModel
from accounts.models import UserModel


class PaymentMethodType(models.TextChoices):
    CREDIT_CARD = 'credit_card', _('Credit Card')
    DEBIT_CARD = 'debit_card', _('Debit Card')
    BANK_TRANSFER = 'bank_transfer', _('Bank Transfer')
    DIGITAL_WALLET = 'digital_wallet', _('Digital Wallet')


class InvoiceStatus(models.TextChoices):
    DRAFT = 'draft', _('Draft')
    SENT = 'sent', _('Sent')
    PAID = 'paid', _('Paid')
    OVERDUE = 'overdue', _('Overdue')
    CANCELLED = 'cancelled', _('Cancelled')


class PaymentStatus(models.TextChoices):
    PENDING = 'pending', _('Pending')
    PROCESSING = 'processing', _('Processing')
    COMPLETED = 'completed', _('Completed')
    FAILED = 'failed', _('Failed')
    CANCELLED = 'cancelled', _('Cancelled')
    REFUNDED = 'refunded', _('Refunded')


class PaymentMethod(AbstractSoftDeleteModel, AbstractTimestampedModel):
    """Payment methods for users."""
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='payment_methods')
    
    # Payment method details
    method_type = models.CharField(_("Method Type"), max_length=20, choices=PaymentMethodType.choices)
    
    # Card information (encrypted)
    card_last4 = models.CharField(_("Last 4 Digits"), max_length=4, blank=True)
    card_brand = models.CharField(_("Card Brand"), max_length=20, blank=True)
    card_exp_month = models.PositiveIntegerField(_("Expiry Month"), null=True, blank=True)
    card_exp_year = models.PositiveIntegerField(_("Expiry Year"), null=True, blank=True)
    
    # Bank information
    bank_name = models.CharField(_("Bank Name"), max_length=100, blank=True)
    account_last4 = models.CharField(_("Last 4 Account Digits"), max_length=4, blank=True)
    
    # Digital wallet
    wallet_type = models.CharField(_("Wallet Type"), max_length=50, blank=True)
    wallet_id = models.CharField(_("Wallet ID"), max_length=100, blank=True)
    
    # Status
    is_default = models.BooleanField(_("Default Method"), default=False)
    is_active = models.BooleanField(_("Active"), default=True)
    
    # External payment processor
    processor_token = models.CharField(_("Processor Token"), max_length=255, blank=True)
    
    class Meta:
        verbose_name = _("Payment Method")
        verbose_name_plural = _("Payment Methods")
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        if self.method_type in ['credit_card', 'debit_card']:
            return f"{self.get_method_type_display()} ****{self.card_last4}... [#{self.id}]"
        elif self.method_type == 'bank_transfer':
            return f"{self.bank_name} ****{self.account_last4}... [#{self.id}]"
        else:
            return f"{self.get_method_type_display()}... [#{self.id}]"


class Invoice(AbstractSoftDeleteModel, AbstractTimestampedModel):
    """Invoices for orders and services."""
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='invoices')
    client = models.ForeignKey('users.ClientProfile', on_delete=models.CASCADE, related_name='invoices')
    provider = models.ForeignKey('users.ServiceProviderProfile', on_delete=models.CASCADE, related_name='invoices')
    
    # Invoice details
    invoice_number = models.CharField(_("Invoice Number"), max_length=50, unique=True)
    invoice_date = models.DateField(_("Invoice Date"), auto_now_add=True)
    due_date = models.DateField(_("Due Date"), null=True, blank=True)
    
    # Amounts
    subtotal = models.DecimalField(_("Subtotal"), max_digits=10, decimal_places=2)
    platform_fee = models.DecimalField(_("Platform Fee"), max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(_("Total Amount"), max_digits=10, decimal_places=2)
    
    # Status
    status = models.CharField(_("Status"), max_length=20, choices=InvoiceStatus.choices, default=InvoiceStatus.DRAFT)
    
    # Payment
    paid_amount = models.DecimalField(_("Paid Amount"), max_digits=10, decimal_places=2, default=0)
    paid_date = models.DateTimeField(_("Paid Date"), null=True, blank=True)
    
    # Notes
    notes = models.TextField(_("Notes"), blank=True)
    
    class Meta:
        verbose_name = _("Invoice")
        verbose_name_plural = _("Invoices")
        ordering = ['-invoice_date']
    
    def __str__(self):
        return f"Invoice #{self.invoice_number} - {self.order.title}... [#{self.id}]"
    
    def save(self, *args, **kwargs):
        """Auto-calculate total amount."""
        self.total_amount = self.subtotal + self.platform_fee
        super().save(*args, **kwargs)


class Payment(AbstractSoftDeleteModel, AbstractTimestampedModel):
    """Payment transactions."""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, related_name='payments')
    
    # Payment details
    payment_id = models.CharField(_("Payment ID"), max_length=100, unique=True)
    amount = models.DecimalField(_("Amount"), max_digits=10, decimal_places=2)
    currency = models.CharField(_("Currency"), default='USD')
    
    # Status
    status = models.CharField(_("Status"), max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    
    # Stripe integration
    stripe_payment_intent_id = models.CharField(_("Stripe Payment Intent ID"), max_length=255, blank=True)
    stripe_charge_id = models.CharField(_("Stripe Charge ID"), max_length=255, blank=True)
    
    # Timestamps
    processed_at = models.DateTimeField(_("Processed At"), null=True, blank=True)
    failed_at = models.DateTimeField(_("Failed At"), null=True, blank=True)
    
    # Error handling
    error_message = models.TextField(_("Error Message"), blank=True)
    
    # Refund information
    refund_amount = models.DecimalField(_("Refund Amount"), max_digits=10, decimal_places=2, default=0)
    refund_reason = models.CharField(_("Refund Reason"), max_length=100, blank=True)
    refunded_at = models.DateTimeField(_("Refunded At"), null=True, blank=True)
    
    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment {self.payment_id} - ${self.amount}... [#{self.id}]"


class StripeWebhookEvent(AbstractTimestampedModel):
    """Stripe webhook events for tracking."""
    stripe_event_id = models.CharField(_("Stripe Event ID"), max_length=255, unique=True)
    event_type = models.CharField(_("Event Type"), max_length=100)
    event_data = models.JSONField(_("Event Data"), default=dict)
    
    # Processing status
    processed = models.BooleanField(_("Processed"), default=False)
    processed_at = models.DateTimeField(_("Processed At"), null=True, blank=True)
    
    # Error handling
    error_message = models.TextField(_("Error Message"), blank=True)
    
    class Meta:
        verbose_name = _("Stripe Webhook Event")
        verbose_name_plural = _("Stripe Webhook Events")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.event_type} - {self.stripe_event_id}... [#{self.id}]"

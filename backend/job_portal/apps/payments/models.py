from django.db import models
from django.utils.translation import gettext_lazy as _
from utils.abstract_models import AbstractSoftDeleteModel, AbstractTimestampedModel
from accounts.models import UserModel


class PaymentMethod(AbstractSoftDeleteModel, AbstractTimestampedModel):
    """Payment methods for users."""
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='payment_methods')
    
    # Payment method details
    method_type = models.CharField(_("Method Type"), max_length=20, choices=[
        ('credit_card', _('Credit Card')),
        ('debit_card', _('Debit Card')),
        ('bank_transfer', _('Bank Transfer')),
        ('digital_wallet', _('Digital Wallet')),
        ('crypto', _('Cryptocurrency')),
    ])
    
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
    tax_amount = models.DecimalField(_("Tax Amount"), max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(_("Discount Amount"), max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(_("Total Amount"), max_digits=10, decimal_places=2)
    
    # Status
    status = models.CharField(_("Status"), max_length=20, choices=[
        ('draft', _('Draft')),
        ('sent', _('Sent')),
        ('paid', _('Paid')),
        ('overdue', _('Overdue')),
        ('cancelled', _('Cancelled')),
    ], default='draft')
    
    # Payment
    paid_amount = models.DecimalField(_("Paid Amount"), max_digits=10, decimal_places=2, default=0)
    paid_date = models.DateTimeField(_("Paid Date"), null=True, blank=True)
    
    # Notes
    notes = models.TextField(_("Notes"), blank=True)
    terms_conditions = models.TextField(_("Terms & Conditions"), blank=True)
    
    class Meta:
        verbose_name = _("Invoice")
        verbose_name_plural = _("Invoices")
        ordering = ['-invoice_date']
    
    def __str__(self):
        return f"Invoice #{self.invoice_number} - {self.order.title}... [#{self.id}]"


class InvoiceItem(AbstractTimestampedModel):
    """Individual items on invoices."""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    
    # Item details
    description = models.CharField(_("Description"), max_length=200)
    quantity = models.PositiveIntegerField(_("Quantity"), default=1)
    unit_price = models.DecimalField(_("Unit Price"), max_digits=10, decimal_places=2)
    total_price = models.DecimalField(_("Total Price"), max_digits=10, decimal_places=2)
    
    # Service reference
    service_addon = models.ForeignKey('core.ServiceAddon', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = _("Invoice Item")
        verbose_name_plural = _("Invoice Items")
        ordering = ['id']
    
    def __str__(self):
        return f"{self.description} - {self.quantity} x ${self.unit_price}... [#{self.id}]"


class Payment(AbstractSoftDeleteModel, AbstractTimestampedModel):
    """Payment transactions."""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, related_name='payments')
    
    # Payment details
    payment_id = models.CharField(_("Payment ID"), max_length=100, unique=True)
    amount = models.DecimalField(_("Amount"), max_digits=10, decimal_places=2)
    currency = models.CharField(_("Currency"), max_length=3, default='USD')
    
    # Status
    status = models.CharField(_("Status"), max_length=20, choices=[
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled')),
        ('refunded', _('Refunded')),
    ], default='pending')
    
    # Transaction details
    transaction_id = models.CharField(_("Transaction ID"), max_length=100, blank=True)
    processor_response = models.JSONField(_("Processor Response"), default=dict)
    
    # Timestamps
    processed_at = models.DateTimeField(_("Processed At"), null=True, blank=True)
    failed_at = models.DateTimeField(_("Failed At"), null=True, blank=True)
    
    # Error handling
    error_message = models.TextField(_("Error Message"), blank=True)
    retry_count = models.PositiveIntegerField(_("Retry Count"), default=0)
    
    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment {self.payment_id} - ${self.amount}... [#{self.id}]"


class Refund(AbstractTimestampedModel):
    """Refunds for payments."""
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='refunds')
    
    # Refund details
    refund_id = models.CharField(_("Refund ID"), max_length=100, unique=True)
    amount = models.DecimalField(_("Refund Amount"), max_digits=10, decimal_places=2)
    reason = models.CharField(_("Refund Reason"), max_length=100)
    description = models.TextField(_("Description"), blank=True)
    
    # Status
    status = models.CharField(_("Status"), max_length=20, choices=[
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
    ], default='pending')
    
    # Processing
    processed_at = models.DateTimeField(_("Processed At"), null=True, blank=True)
    processor_response = models.JSONField(_("Processor Response"), default=dict)
    
    # Admin handling
    approved_by = models.ForeignKey(UserModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='refunds_approved')
    approved_at = models.DateTimeField(_("Approved At"), null=True, blank=True)
    
    class Meta:
        verbose_name = _("Refund")
        verbose_name_plural = _("Refunds")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Refund {self.refund_id} - ${self.amount}... [#{self.id}]"


class Subscription(AbstractSoftDeleteModel, AbstractTimestampedModel):
    """Subscription plans for service providers."""
    provider = models.ForeignKey('users.ServiceProviderProfile', on_delete=models.CASCADE, related_name='subscriptions')
    
    # Plan details
    plan_name = models.CharField(_("Plan Name"), max_length=100)
    plan_type = models.CharField(_("Plan Type"), max_length=20, choices=[
        ('basic', _('Basic')),
        ('premium', _('Premium')),
        ('enterprise', _('Enterprise')),
    ])
    
    # Pricing
    monthly_price = models.DecimalField(_("Monthly Price"), max_digits=10, decimal_places=2)
    yearly_price = models.DecimalField(_("Yearly Price"), max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Features
    features = models.JSONField(_("Features"), default=list)
    max_orders_per_month = models.PositiveIntegerField(_("Max Orders per Month"), null=True, blank=True)
    
    # Status
    status = models.CharField(_("Status"), max_length=20, choices=[
        ('active', _('Active')),
        ('cancelled', _('Cancelled')),
        ('expired', _('Expired')),
        ('suspended', _('Suspended')),
    ], default='active')
    
    # Billing cycle
    billing_cycle = models.CharField(_("Billing Cycle"), max_length=20, choices=[
        ('monthly', _('Monthly')),
        ('yearly', _('Yearly')),
    ], default='monthly')
    
    # Dates
    start_date = models.DateField(_("Start Date"))
    end_date = models.DateField(_("End Date"), null=True, blank=True)
    next_billing_date = models.DateField(_("Next Billing Date"), null=True, blank=True)
    
    class Meta:
        verbose_name = _("Subscription")
        verbose_name_plural = _("Subscriptions")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.provider.user_profile.user.name} - {self.plan_name}... [#{self.id}]"

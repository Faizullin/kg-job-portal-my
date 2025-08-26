from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from .models import Payment, PaymentMethod, Invoice, PaymentProvider, StripeWebhookEvent


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'invoice', 'payment_method', 'amount', 'currency', 'status',
        'transaction_id', 'created_at'
    ]
    list_filter = ['status', 'currency', 'created_at']
    search_fields = ['payment_id', 'transaction_id', 'invoice__invoice_number']
    ordering = ['-created_at']
    list_editable = ['status']
    raw_id_fields = ['invoice', 'payment_method']
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('invoice', 'payment_method', 'amount', 'currency', 'status')
        }),
        ('Transaction Details', {
            'fields': ('payment_id', 'transaction_id', 'processor_response')
        }),
        ('Timestamps', {
            'fields': ('processed_at', 'failed_at')
        }),
        ('Refund Information', {
            'fields': ('refund_amount', 'refund_reason', 'refunded_at'),
            'classes': ('collapse',)
        }),
        ('Error Handling', {
            'fields': ('error_message', 'retry_count'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order', 'user', 'payment_method')
    
    def has_change_permission(self, request, obj=None):
        """Only superusers, payment managers, and finance managers can modify payments."""
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name__in=['Payment Managers', 'Finance Managers']).exists()
    
    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete payments."""
        return request.user.is_superuser


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'method_type', 'card_last4', 'card_brand',
        'card_exp_month', 'card_exp_year', 'is_default', 'is_active'
    ]
    list_filter = ['method_type', 'card_brand', 'is_default', 'is_active', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'card_last4']
    ordering = ['-is_default', '-created_at']
    list_editable = ['is_default', 'is_active']
    raw_id_fields = ['user']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'method_type')
        }),
        ('Card Details', {
            'fields': ('card_last4', 'card_brand', 'card_exp_month', 'card_exp_year')
        }),
        ('Settings', {
            'fields': ('is_default', 'is_active')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    def has_change_permission(self, request, obj=None):
        """Only superusers, payment managers, and finance managers can modify payment methods."""
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name__in=['Payment Managers', 'Finance Managers']).exists()
    
    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete payment methods."""
        return request.user.is_superuser


@admin.register(PaymentProvider)
class PaymentProviderAdmin(admin.ModelAdmin):
    """
    Admin for payment providers with secure field handling.
    """
    list_display = [
        'id', 'name', 'is_active', 'test_mode', 'supported_currencies_display',
        'created_at'
    ]
    list_filter = ['is_active', 'test_mode', 'created_at']
    search_fields = ['name']
    ordering = ['name']
    list_editable = ['is_active', 'test_mode']
    
    fieldsets = (
        ('Provider Information', {
            'fields': ('name', 'is_active', 'test_mode')
        }),
        ('Configuration', {
            'fields': ('api_key', 'secret_key', 'webhook_secret'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('supported_currencies', 'config_data')
        }),
    )
    
    def supported_currencies_display(self, obj):
        """Display supported currencies in a readable format."""
        if obj.supported_currencies:
            return ', '.join(obj.supported_currencies)
        return 'None'
    supported_currencies_display.short_description = 'Supported Currencies'
    
    def get_fieldsets(self, request, obj=None):
        """Show sensitive fields only to superusers or payment managers."""
        if request.user.is_superuser or self._has_payment_manager_permission(request.user):
            return self.fieldsets
        else:
            # Hide sensitive configuration fields
            return (
                ('Provider Information', {
                    'fields': ('name', 'is_active', 'test_mode')
                }),
                ('Settings', {
                    'fields': ('supported_currencies',)
                }),
            )
    
    def _has_payment_manager_permission(self, user):
        """Check if user has payment manager permissions."""
        return user.groups.filter(name__in=['Payment Managers', 'Finance Managers']).exists()
    
    def has_change_permission(self, request, obj=None):
        """Only superusers and payment managers can change payment providers."""
        if request.user.is_superuser:
            return True
        return self._has_payment_manager_permission(request.user)
    
    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete payment providers."""
        return request.user.is_superuser


@admin.register(StripeWebhookEvent)
class StripeWebhookEventAdmin(admin.ModelAdmin):
    """
    Admin for Stripe webhook events.
    """
    list_display = [
        'id', 'stripe_event_id', 'event_type', 'processed', 'processed_at',
        'retry_count', 'created_at'
    ]
    list_filter = ['processed', 'event_type', 'created_at']
    search_fields = ['stripe_event_id', 'event_type']
    ordering = ['-created_at']
    readonly_fields = ['stripe_event_id', 'event_type', 'event_data', 'created_at']
    
    fieldsets = (
        ('Event Information', {
            'fields': ('stripe_event_id', 'event_type', 'created_at')
        }),
        ('Processing Status', {
            'fields': ('processed', 'processed_at', 'retry_count')
        }),
        ('Event Data', {
            'fields': ('event_data',),
            'classes': ('collapse',)
        }),
        ('Error Handling', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Webhook events are created automatically, not manually."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Only superusers and payment managers can modify webhook events."""
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name__in=['Payment Managers', 'Finance Managers']).exists()


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'order', 'invoice_number', 'status', 'subtotal', 'tax_amount',
        'discount_amount', 'total_amount_display', 'due_date', 'paid_date'
    ]
    list_filter = ['status', 'due_date', 'created_at']
    search_fields = ['invoice_number', 'order__title']
    ordering = ['-created_at']
    list_editable = ['status']
    raw_id_fields = ['order']
    
    fieldsets = (
        ('Invoice Information', {
            'fields': ('order', 'invoice_number', 'status')
        }),
        ('Financial Details', {
            'fields': ('subtotal', 'tax_amount', 'discount_amount', 'total_amount')
        }),
        ('Dates', {
            'fields': ('due_date', 'paid_date')
        }),
    )
    
    def total_amount_display(self, obj):
        return f"${obj.total_amount:.2f}"
    total_amount_display.short_description = 'Total Amount'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order')
    
    def has_change_permission(self, request, obj=None):
        """Only superusers, payment managers, and finance managers can modify invoices."""
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name__in=['Payment Managers', 'Finance Managers']).exists()
    
    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete invoices."""
        return request.user.is_superuser


# Refund functionality is now integrated into the Payment model

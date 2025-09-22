from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from .models import Payment, PaymentMethod, Invoice, StripeWebhookEvent
from django.utils import timezone


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'invoice', 'payment_method', 'amount', 'currency', 'status',
        'stripe_payment_intent_id', 'created_at'
    ]
    list_filter = ['status', 'currency', 'created_at']
    search_fields = ['payment_id', 'stripe_payment_intent_id', 'invoice__invoice_number']
    ordering = ['-created_at']
    list_editable = ['status']
    raw_id_fields = ['invoice', 'payment_method']
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('invoice', 'payment_method', 'amount', 'currency', 'status')
        }),
        ('Stripe Integration', {
            'fields': ('stripe_payment_intent_id', 'stripe_charge_id')
        }),
        ('Timestamps', {
            'fields': ('processed_at', 'failed_at')
        }),
        ('Refund Information', {
            'fields': ('refund_amount', 'refund_reason', 'refunded_at'),
            'classes': ('collapse',)
        }),
        ('Error Handling', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('invoice__order', 'payment_method__user')
    
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


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'invoice_number', 'order', 'client', 'provider',
        'subtotal', 'platform_fee', 'total_amount', 'status', 'created_at'
    ]
    list_filter = ['status', 'created_at', 'due_date']
    search_fields = ['invoice_number', 'order__title']
    ordering = ['-created_at']
    list_editable = ['status']
    raw_id_fields = ['order', 'client', 'provider']
    
    fieldsets = (
        ('Invoice Information', {
            'fields': ('invoice_number', 'order', 'client', 'provider')
        }),
        ('Amounts', {
            'fields': ('subtotal', 'platform_fee', 'total_amount')
        }),
        ('Dates', {
            'fields': ('invoice_date', 'due_date', 'paid_date')
        }),
        ('Status', {
            'fields': ('status', 'paid_amount')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order', 'client__user_profile', 'provider__user_profile')
    
    def has_change_permission(self, request, obj=None):
        """Only superusers, payment managers, and finance managers can modify invoices."""
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name__in=['Payment Managers', 'Finance Managers']).exists()
    
    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete invoices."""
        return request.user.is_superuser


@admin.register(StripeWebhookEvent)
class StripeWebhookEventAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'stripe_event_id', 'event_type', 'processed', 'created_at'
    ]
    list_filter = ['event_type', 'processed', 'created_at']
    search_fields = ['stripe_event_id', 'event_type']
    ordering = ['-created_at']
    list_editable = ['processed']
    readonly_fields = ['stripe_event_id', 'event_type', 'event_data', 'created_at']
    
    fieldsets = (
        ('Event Information', {
            'fields': ('stripe_event_id', 'event_type', 'event_data')
        }),
        ('Processing Status', {
            'fields': ('processed', 'processed_at')
        }),
        ('Error Information', {
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
        return request.user.groups.filter(name__in=['Payment Managers']).exists()
    
    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete webhook events."""
        return request.user.is_superuser


# Custom admin actions
@admin.action(description="Mark selected payments as completed")
def mark_payments_completed(modeladmin, request, queryset):
    updated = queryset.update(status='completed', processed_at=timezone.now())
    modeladmin.message_user(request, f"{updated} payments marked as completed.")

@admin.action(description="Mark selected invoices as paid")
def mark_invoices_paid(modeladmin, request, queryset):
    updated = queryset.update(status='paid', paid_date=timezone.now())
    modeladmin.message_user(request, f"{updated} invoices marked as paid.")

# Add actions to admin classes
PaymentAdmin.actions = [mark_payments_completed]
InvoiceAdmin.actions = [mark_invoices_paid]

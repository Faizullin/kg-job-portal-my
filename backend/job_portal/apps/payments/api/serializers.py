from rest_framework import serializers
from utils.serializers import (
    AbstractTimestampedModelSerializer,
    AbstractSoftDeleteModelSerializer,
    AbstractChoiceFieldSerializerMixin,
    AbstractComputedFieldSerializerMixin
)
from ..models import Payment, PaymentMethod, Invoice, PaymentProvider, StripeWebhookEvent


class PaymentMethodSerializer(AbstractTimestampedModelSerializer, AbstractChoiceFieldSerializerMixin):
    payment_type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'user', 'payment_type', 'payment_type_display', 'card_last4',
            'card_brand', 'expiry_month', 'expiry_year', 'is_default', 'is_active'
        ]
    
    def get_payment_type_display(self, obj):
        return self.get_choice_display(obj, 'payment_type')


class InvoiceSerializer(AbstractTimestampedModelSerializer, AbstractChoiceFieldSerializerMixin):
    status_display = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'order', 'invoice_number', 'status', 'status_display',
            'subtotal', 'tax_amount', 'commission_amount', 'total_amount',
            'due_date', 'paid_date', 'created_at'
        ]
    
    def get_status_display(self, obj):
        return self.get_choice_display(obj, 'status')
    
    def get_total_amount(self, obj):
        return obj.subtotal + obj.tax_amount + obj.commission_amount


class PaymentSerializer(AbstractTimestampedModelSerializer, AbstractChoiceFieldSerializerMixin):
    payment_method = PaymentMethodSerializer(read_only=True)
    status_display = serializers.SerializerMethodField()
    payment_type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'user', 'amount', 'currency', 'status', 'status_display',
            'payment_type', 'payment_type_display', 'payment_method', 'transactions',
            'gateway_fee', 'net_amount', 'created_at', 'updated_at'
        ]
    
    def get_status_display(self, obj):
        return self.get_choice_display(obj, 'status')
    
    def get_payment_type_display(self, obj):
        return self.get_choice_display(obj, 'payment_type')


class PaymentCreateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = Payment
        fields = ['order', 'amount', 'currency', 'payment_method', 'payment_type']


class PaymentMethodCreateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ['payment_type', 'card_last4', 'card_brand', 'expiry_month', 'expiry_year']


class PaymentMethodUpdateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ['is_default', 'is_active']


class InvoiceCreateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = Invoice
        fields = ['order', 'subtotal', 'tax_amount', 'commission_amount', 'due_date']

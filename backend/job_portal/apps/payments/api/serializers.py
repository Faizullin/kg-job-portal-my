from rest_framework import serializers
from utils.serializers import (
    AbstractChoiceFieldSerializerMixin,
    AbstractTimestampedModelSerializer,
)

from ..models import Invoice, Payment, PaymentMethod, StripeWebhookEvent


class PaymentMethodSerializer(
    AbstractTimestampedModelSerializer, AbstractChoiceFieldSerializerMixin
):
    method_type_display = serializers.SerializerMethodField()

    class Meta:
        model = PaymentMethod
        fields = [
            "id",
            "user",
            "method_type",
            "method_type_display",
            "card_last4",
            "card_brand",
            "card_exp_month",
            "card_exp_year",
            "is_default",
            "is_active",
        ]

    def get_method_type_display(self, obj):
        return self.get_choice_display(obj, "method_type")


class InvoiceSerializer(
    AbstractTimestampedModelSerializer, AbstractChoiceFieldSerializerMixin
):
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            "id",
            "order",
            "invoice_number",
            "status",
            "status_display",
            "subtotal",
            "platform_fee",
            "total_amount",
            "due_date",
            "paid_date",
            "created_at",
        ]

    def get_status_display(self, obj):
        return self.get_choice_display(obj, "status")


class PaymentSerializer(
    AbstractTimestampedModelSerializer, AbstractChoiceFieldSerializerMixin
):
    payment_method = PaymentMethodSerializer(read_only=True)
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            "id",
            "invoice",
            "amount",
            "currency",
            "status",
            "status_display",
            "payment_method",
            "stripe_payment_intent_id",
            "stripe_charge_id",
            "processed_at",
            "created_at",
            "updated_at",
        ]

    def get_status_display(self, obj):
        return self.get_choice_display(obj, "status")


class PaymentCreateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = Payment
        fields = ["invoice", "amount", "currency", "payment_method"]


class PaymentMethodCreateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = [
            "method_type",
            "card_last4",
            "card_brand",
            "card_exp_month",
            "card_exp_year",
        ]


class PaymentMethodUpdateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ["is_default", "is_active"]


class InvoiceCreateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = Invoice
        fields = ["order", "subtotal", "platform_fee", "due_date"]


class StripeWebhookEventSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = StripeWebhookEvent
        fields = [
            "id",
            "stripe_event_id",
            "event_type",
            "event_data",
            "processed",
            "processed_at",
            "error_message",
            "created_at",
        ]


class WebhookResponseSerializer(serializers.Serializer):
    """Serializer for webhook response."""

    status = serializers.CharField(help_text="Webhook processing status")
    message = serializers.CharField(required=False, help_text="Additional message")


class WebhookRetryResponseSerializer(serializers.Serializer):
    """Serializer for webhook retry response."""

    status = serializers.CharField(help_text="Retry processing status")
    message = serializers.CharField(required=False, help_text="Additional message")

# DRF imports
from rest_framework import serializers

# Local imports
from utils.serializers import (
    AbstractTimestampedModelSerializer,
    AbstractChoiceFieldSerializerMixin
)
from ..models import Order, Bid, OrderAssignment


class BidSerializer(AbstractTimestampedModelSerializer, AbstractChoiceFieldSerializerMixin):
    provider_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Bid
        fields = [
            'id', 'order', 'provider', 'provider_name', 'amount', 'description',
            'estimated_duration', 'status', 'is_negotiable',
            'terms_conditions', 'created_at'
        ]
    
    def get_provider_name(self, obj):
        if obj.provider and obj.provider.user_profile and obj.provider.user_profile.user:
            return obj.provider.user_profile.user.username
        return "Unknown Provider"



class OrderSerializer(AbstractTimestampedModelSerializer, AbstractChoiceFieldSerializerMixin):
    bids = BidSerializer(many=True, read_only=True)
    client_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'client', 'client_name', 'service_subcategory', 'title', 'description', 'status',
            'location', 'city', 'state', 'country', 'postal_code', 'service_date', 'service_time',
            'urgency', 'budget_min', 'budget_max', 'final_price', 'bids',
            'attachments', 'special_requirements', 'is_featured', 'created_at', 'updated_at'
        ]
    
    def get_client_name(self, obj):
        if obj.client and obj.client.user_profile and obj.client.user_profile.user:
            return obj.client.user_profile.user.username
        return "Unknown Client"


class OrderCreateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = Order
        fields = [
            'service_subcategory', 'title', 'description', 'location', 'city', 'state',
            'country', 'postal_code', 'service_date', 'service_time', 'urgency',
            'budget_min', 'budget_max', 'special_requirements'
        ]


class OrderUpdateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = Order
        fields = ['title', 'description', 'location', 'city', 'state', 'country', 'postal_code', 'service_date', 'service_time', 'urgency', 'budget_min', 'budget_max', 'special_requirements', "status"]




class BidCreateUpdateSerializer(AbstractTimestampedModelSerializer):
    """Unified serializer for bid creation and updates."""
    class Meta:
        model = Bid
        fields = ['amount', 'description', 'estimated_duration', 'terms_conditions', 'is_negotiable']


class BidActionSerializer(serializers.Serializer):
    """Serializer for bid actions (accept/reject/withdraw)."""
    reason = serializers.CharField(max_length=500, required=False, help_text="Reason for rejection/withdrawal")


class OrderAssignmentSerializer(AbstractTimestampedModelSerializer):
    order_title = serializers.SerializerMethodField()
    provider_name = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderAssignment
        fields = [
            'id', 'order', 'order_title', 'provider', 'provider_name', 'accepted_bid',
            'assigned_at', 'start_date', 'start_time', 'progress_notes',
            'completion_notes', 'client_rating', 'client_review', 'created_at'
        ]
        read_only_fields = ('assigned_at', 'created_at')
    
    def get_order_title(self, obj):
        return obj.order.title if obj.order else 'Unknown Order'
    
    def get_provider_name(self, obj):
        if obj.provider and obj.provider.user_profile and obj.provider.user_profile.user:
            return obj.provider.user_profile.user.username
        return "Unknown Provider"



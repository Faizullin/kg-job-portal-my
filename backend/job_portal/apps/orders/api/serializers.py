from rest_framework import serializers
from utils.serializers import (
    AbstractTimestampedModelSerializer,
    AbstractSoftDeleteModelSerializer,
    AbstractChoiceFieldSerializerMixin,
    AbstractComputedFieldSerializerMixin
)
from ..models import Order, OrderAddon, OrderPhoto, Bid, OrderAssignment, OrderDispute


class OrderAddonSerializer(AbstractTimestampedModelSerializer):
    addon_name = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderAddon
        fields = [
            'id', 'order', 'addon', 'addon_name', 'quantity', 'price'
        ]
    
    def get_addon_name(self, obj):
        return obj.addon.name if obj.addon else 'Unknown Addon'


class OrderPhotoSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = OrderPhoto
        fields = [
            'id', 'order', 'photo_url', 'caption', 'is_primary', 'created_at'
        ]


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
            return obj.provider.user_profile.user.name
        return "Unknown Provider"

class OrderDisputeSerializer(AbstractTimestampedModelSerializer, AbstractChoiceFieldSerializerMixin):
    dispute_type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderDispute
        fields = [
            'id', 'order', 'raised_by', 'dispute_type', 'dispute_type_display', 'description',
            'evidence', 'status', 'admin_notes', 'resolved_by',
            'resolved_at', 'resolution', 'created_at'
        ]
    
    def get_dispute_type_display(self, obj):
        return self.get_choice_display(obj, 'dispute_type')


class OrderSerializer(AbstractTimestampedModelSerializer, AbstractChoiceFieldSerializerMixin):
    addons = OrderAddonSerializer(many=True, read_only=True)
    photos = OrderPhotoSerializer(many=True, read_only=True)
    bids = BidSerializer(many=True, read_only=True)
    client_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'client', 'client_name', 'service_subcategory', 'title', 'description', 'status',
            'location', 'city', 'state', 'country', 'postal_code', 'service_date', 'service_time',
            'urgency', 'budget_min', 'budget_max', 'final_price', 'addons', 'photos', 'bids',
            'attachments', 'special_requirements', 'is_featured', 'created_at', 'updated_at'
        ]
    
    def get_client_name(self, obj):
        if obj.client and obj.client.user_profile and obj.client.user_profile.user:
            return obj.client.user_profile.user.name
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
        fields = ['title', 'description', 'location', 'city', 'state', 'country', 'postal_code', 'service_date', 'service_time', 'urgency', 'budget_min', 'budget_max', 'special_requirements']


class OrderAddonCreateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = OrderAddon
        fields = ['addon', 'quantity', 'price']


class OrderAddonUpdateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = OrderAddon
        fields = ['quantity', 'price']


class BidCreateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = Bid
        fields = ['amount', 'description', 'estimated_duration', 'terms_conditions', 'is_negotiable']


class BidUpdateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = Bid
        fields = ['amount', 'description', 'estimated_duration', 'terms_conditions', 'is_negotiable']


class OrderDisputeCreateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = OrderDispute
        fields = ['dispute_type', 'description', 'evidence']


class OrderDisputeUpdateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = OrderDispute
        fields = ['status', 'admin_notes', 'resolution']

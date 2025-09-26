from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from utils.serializers import AbstractTimestampedModelSerializer, AbstractChoiceFieldSerializerMixin
from ..models import Review, AppFeedback


class ReviewSerializer(AbstractTimestampedModelSerializer, AbstractChoiceFieldSerializerMixin):
    """Serializer for reading review data with OpenAPI support."""
    reviewer_name = serializers.SerializerMethodField()
    reviewer_email = serializers.SerializerMethodField()
    provider_name = serializers.SerializerMethodField()
    provider_email = serializers.SerializerMethodField()
    order_id = serializers.SerializerMethodField()
    order_title = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = [
            'id',
            'order_id',
            'order_title',
            'reviewer_name',
            'reviewer_email',
            'provider_name',
            'provider_email',
            'overall_rating',
            'title',
            'comment',
            'is_verified',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'is_verified',
            'created_at',
            'updated_at'
        ]
    
    @extend_schema_field(serializers.CharField())
    def get_reviewer_name(self, obj):
        return obj.reviewer.get_full_name() or obj.reviewer.username if obj.reviewer else "Unknown"
    
    @extend_schema_field(serializers.EmailField())
    def get_reviewer_email(self, obj):
        return obj.reviewer.email if obj.reviewer else None
    
    @extend_schema_field(serializers.CharField())
    def get_provider_name(self, obj):
        if obj.provider and obj.provider.user_profile and obj.provider.user_profile.user:
            return obj.provider.user_profile.user.get_full_name() or obj.provider.user_profile.user.username
        return "Unknown Provider"
    
    @extend_schema_field(serializers.EmailField())
    def get_provider_email(self, obj):
        if obj.provider and obj.provider.user_profile and obj.provider.user_profile.user:
            return obj.provider.user_profile.user.email
        return None
    
    @extend_schema_field(serializers.IntegerField())
    def get_order_id(self, obj):
        return obj.order.id if obj.order else None
    
    @extend_schema_field(serializers.CharField())
    def get_order_title(self, obj):
        return obj.order.title if obj.order else None


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new reviews with OpenAPI documentation."""
    
    class Meta:
        model = Review
        fields = [
            'order',
            'provider',
            'overall_rating',
            'title',
            'comment'
        ]
        extra_kwargs = {
            'overall_rating': {
                'help_text': 'Rating from 1 to 5 stars',
                'min_value': 1,
                'max_value': 5
            },
            'title': {
                'help_text': 'Brief title for the review',
                'max_length': 200
            },
            'comment': {
                'help_text': 'Detailed review comment',
                'max_length': 1000
            }
        }
    
    def validate_overall_rating(self, value):
        """Validate overall rating is between 1 and 5."""
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Overall rating must be between 1 and 5.")
        return value
    
    def validate(self, attrs):
        """Validate that the order belongs to the provider and user can review it."""
        order = attrs.get('order')
        provider = attrs.get('provider')
        
        if order and provider:
            # Check if the order has an assignment and belongs to the provider
            if not hasattr(order, 'assignment') or not order.assignment:
                raise serializers.ValidationError(
                    "The order has not been assigned to any provider."
                )
            
            if order.assignment.provider != provider:
                raise serializers.ValidationError(
                    "The order does not belong to the specified provider."
                )
            
            # Check if the order is completed
            if order.status != 'completed':
                raise serializers.ValidationError(
                    "You can only review completed orders."
                )
            
            # Check if review already exists for this order
            if Review.objects.filter(order=order, reviewer=self.context['request'].user).exists():
                raise serializers.ValidationError(
                    "You have already reviewed this order."
                )
        
        return attrs


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating existing reviews."""
    
    class Meta:
        model = Review
        fields = [
            'overall_rating',
            'title',
            'comment'
        ]
    
    def validate_overall_rating(self, value):
        """Validate overall rating is between 1 and 5."""
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Overall rating must be between 1 and 5.")
        return value


class ReviewAnalyticsSerializer(serializers.Serializer):
    """Serializer for review analytics data with OpenAPI support."""
    total_reviews = serializers.IntegerField(help_text="Total number of reviews")
    average_rating = serializers.DecimalField(
        max_digits=3, 
        decimal_places=2,
        help_text="Average rating across all reviews"
    )
    rating_distribution = serializers.ListField(
        child=serializers.DictField(),
        help_text="Distribution of ratings (1-5 stars)"
    )


class ClientRatingSerializer(serializers.Serializer):
    """Serializer for client rating from OrderAssignment model."""
    rating = serializers.IntegerField(
        min_value=1,
        max_value=5,
        help_text="Client rating from 1 to 5 stars"
    )
    review = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        help_text="Optional review text about the client"
    )
    
    def validate_rating(self, value):
        """Validate rating is between 1 and 5."""
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


class OrderAssignmentReviewSerializer(serializers.Serializer):
    """Serializer for order assignment with review data."""
    order_id = serializers.IntegerField(help_text="Order ID")
    order_title = serializers.CharField(help_text="Order title")
    provider_name = serializers.CharField(help_text="Provider name")
    client_name = serializers.CharField(help_text="Client name")
    client_rating = serializers.IntegerField(
        allow_null=True,
        help_text="Client rating (1-5 stars)"
    )
    client_review = serializers.CharField(
        allow_null=True,
        allow_blank=True,
        help_text="Client review text"
    )
    provider_rating = serializers.IntegerField(
        allow_null=True,
        help_text="Provider rating (1-5 stars)"
    )
    provider_review = serializers.CharField(
        allow_null=True,
        allow_blank=True,
        help_text="Provider review text"
    )
    completed_at = serializers.DateTimeField(help_text="Order completion date")


class AppFeedbackSerializer(AbstractTimestampedModelSerializer):
    """Serializer for app feedback and rating system."""
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = AppFeedback
        fields = (
            'id', 'user', 'user_name', 'user_email',
            'general_opinion', 'detailed_feedback', 'overall_rating',
            'design_feedback', 'usability_feedback', 'bug_report', 
            'missing_features', 'everything_satisfies',
            'app_version', 'device_info', 'platform',
            'is_reviewed', 'admin_notes', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'user', 'is_reviewed', 'admin_notes', 'created_at', 'updated_at')
    
    def validate_overall_rating(self, value):
        """Validate overall rating is between 1 and 5."""
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Overall rating must be between 1 and 5.")
        return value


class AppFeedbackCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating app feedback."""
    
    class Meta:
        model = AppFeedback
        fields = (
            'general_opinion', 'detailed_feedback', 'overall_rating',
            'design_feedback', 'usability_feedback', 'bug_report', 
            'missing_features', 'everything_satisfies',
            'app_version', 'device_info', 'platform'
        )
    
    def validate_overall_rating(self, value):
        """Validate overall rating is between 1 and 5."""
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Overall rating must be between 1 and 5.")
        return value



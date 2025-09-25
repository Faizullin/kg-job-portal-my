from rest_framework import serializers
from utils.serializers import AbstractTimestampedModelSerializer
from ..models import Review, AppFeedback


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for reading review data."""
    reviewer_name = serializers.CharField(source='reviewer.name', read_only=True)
    reviewer_email = serializers.EmailField(source='reviewer.email', read_only=True)
    provider_name = serializers.CharField(source='provider.user_profile.user.username', read_only=True)
    provider_email = serializers.EmailField(source='provider.user_profile.user.email', read_only=True)
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    order_title = serializers.CharField(source='order.title', read_only=True)
    
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


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new reviews."""
    
    class Meta:
        model = Review
        fields = [
            'order',
            'provider',
            'overall_rating',
            'title',
            'comment'
        ]
    
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
            
            # Check if the order is completed (you might want to add this check)
            if order.status != 'completed':
                raise serializers.ValidationError(
                    "You can only review completed orders."
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
    """Serializer for review analytics data."""
    total_reviews = serializers.IntegerField()
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2)
    rating_distribution = serializers.ListField(
        child=serializers.DictField()
    )


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



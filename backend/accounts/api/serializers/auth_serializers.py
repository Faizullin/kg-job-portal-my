from rest_framework import serializers
from ...models import UserModel, UserRoleTypes


class FireBaseAuthSerializer(serializers.Serializer):
    """Serializer for Firebase authentication request"""
    id_token = serializers.CharField(help_text='Firebase ID token', required=True)


class FirebaseAuthResponseSerializer(serializers.Serializer):
    """Serializer for Firebase authentication response"""
    token = serializers.CharField(help_text='DRF authentication token')
    user = serializers.DictField(help_text='User information')
    message = serializers.CharField(help_text='Authentication success message')


class LogoutResponseSerializer(serializers.Serializer):
    """Serializer for logout response"""
    message = serializers.CharField(help_text='Logout confirmation message')


class UserRoleSelectionSerializer(serializers.Serializer):
    """Serializer for user role selection"""
    user_role = serializers.ChoiceField(choices=UserRoleTypes.choices(), help_text='User role selection')


class ServiceCategoriesSerializer(serializers.Serializer):
    """Serializer for service categories selection"""
    service_categories = serializers.ListField(
        child=serializers.CharField(max_length=100),
        help_text='List of service categories'
    )


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    phone_number = serializers.CharField(max_length=20, required=False)
    user_role = serializers.ChoiceField(choices=UserRoleTypes.choices(), required=False)
    service_categories = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    
    class Meta:
        model = UserModel
        fields = [
            'name', 'email', 'phone_number', 'user_role', 'service_categories', 'description', 'photo_url'
        ]
    
    def validate_phone_number(self, value):
        if value and not value.startswith('+'):
            raise serializers.ValidationError("Phone number must include country code")
        return value


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile display"""
    user_role_display = serializers.CharField(source='get_user_role_display', read_only=True)
    
    class Meta:
        model = UserModel
        fields = [
            'id', 'username', 'name', 'email', 'phone_number', 'user_role', 'user_role_display',
            'description', 'photo_url', 'service_categories', 'rating', 'total_reviews',
            'is_available', 'points', 'day_streak', 'max_day_streak'
        ]
        read_only_fields = ['id', 'username', 'rating', 'total_reviews']
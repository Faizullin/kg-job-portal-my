from rest_framework import serializers

from ...models import UserModel


class ProfileImageUploadSerializer(serializers.ModelSerializer):
    """Serializer for uploading profile images"""

    class Meta:
        model = UserModel
        fields = ('photo',)

    def validate_photo(self, value):
        """Validate uploaded profile image"""
        if value:
            # Check file size (5MB limit for profile images)
            max_size = 5 * 1024 * 1024  # 5MB
            if value.size > max_size:
                raise serializers.ValidationError(
                    "Profile image size must be no more than 5MB."
                )

            # Check file type (images only)
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if hasattr(value, 'content_type') and value.content_type not in allowed_types:
                raise serializers.ValidationError(
                    "Only JPEG, PNG, GIF and WebP images are allowed for profile photos."
                )

            # Check image dimensions (optional - can be added if needed)
            # from PIL import Image
            # img = Image.open(value)
            # if img.width > 2048 or img.height > 2048:
            #     raise serializers.ValidationError(
            #         "Image dimensions must be no larger than 2048x2048 pixels."
            #     )

        return value


class ProfileImageResponseSerializer(serializers.ModelSerializer):
    """Serializer for profile image response"""
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = UserModel
        fields = ('id', 'photo', 'photo_url', 'name')
        read_only_fields = ('id', 'name')

    def get_photo_url(self, obj):
        """Get the full URL for the profile photo"""
        if obj.photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.photo.url)
            return obj.photo.url
        return None

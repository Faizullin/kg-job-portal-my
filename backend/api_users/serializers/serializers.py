from rest_framework import serializers

from api_users.models import UserModel
from api_users.serializers.model_serializers import NotificationSettingsSerializer


class FireBaseAuthSerializer(serializers.Serializer):
    token = serializers.CharField()


class EditUserSettingsSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=20, min_length=2)
    description = serializers.CharField(max_length=80, min_length=2)
    notification_settings = NotificationSettingsSerializer()

    class Meta:
        model = UserModel
        fields = ['name', 'description', 'notification_settings']

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)

        notif_serializer = NotificationSettingsSerializer(instance.notification_settings,
                                                          validated_data.get('notification_settings'),
                                                          partial=True)
        notif_serializer.is_valid(raise_exception=True)
        notif_serializer.save()
        instance.save()
        return instance


class SearchUserSerializer(serializers.Serializer):
    search = serializers.CharField(max_length=50, min_length=1)


class GetUserByIdSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

    def validate_user_id(self, obj):
        try:
            user = UserModel.objects.get(id=obj)
        except UserModel.DoesNotExist:
            raise serializers.ValidationError('User with this id ID does not exist')
        return user

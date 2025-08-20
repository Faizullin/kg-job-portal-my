from django.contrib.auth import get_user_model
from rest_framework import serializers

UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = [
            "id",
            "username",
            "email",
            "date_joined",
            "is_active",
            "is_staff",
            "is_superuser",
            "is_paid",
            "user_type",
        ]

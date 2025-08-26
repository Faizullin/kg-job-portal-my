from rest_framework import serializers
from django.contrib.auth import get_user_model
from utils.serializers import AbstractTimestampedModelSerializer
from utils.abstract_models import AbstractTimestampedModel
from ..models import UserProfile, ServiceProviderProfile, ClientProfile, UserVerification, ServiceProviderService


class ServiceProviderSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = ServiceProviderProfile
        fields = '__all__'


class ClientSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = ClientProfile
        fields = '__all__'


class UserProfileSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class UserProfileUpdateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class ServiceProviderUpdateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = ServiceProviderProfile
        fields = '__all__'


class ClientUpdateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = ClientProfile
        fields = '__all__'

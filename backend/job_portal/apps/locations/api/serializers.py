from rest_framework import serializers

from utils.serializers import AbstractTimestampedModelSerializer
from ..models import Country, City


class CountrySerializer(AbstractTimestampedModelSerializer):
    """Serializer for Country model."""

    class Meta:
        model = Country
        fields = [
            "id",
            "name",
            "code",
            "created_at",
            "updated_at",
        ]


class CitySerializer(AbstractTimestampedModelSerializer):
    """Serializer for City model."""

    country = CountrySerializer(read_only=True)
    country_name = serializers.CharField(source="country.name", read_only=True)

    class Meta:
        model = City
        fields = [
            "id",
            "name",
            "code",
            "country",
            "country_name",
            "created_at",
            "updated_at",
        ]


class CityListSerializer(AbstractTimestampedModelSerializer):
    """Simplified serializer for city lists."""

    country_name = serializers.CharField(source="country.name", read_only=True)

    class Meta:
        model = City
        fields = [
            "id",
            "name",
            "code",
            "country_name",
        ]


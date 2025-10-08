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
        ]


class CitySerializer(AbstractTimestampedModelSerializer):
    """Serializer for City model."""

    country = CountrySerializer(read_only=True)

    class Meta:
        model = City
        fields = [
            "id",
            "name",
            "code",
            "country",
        ]


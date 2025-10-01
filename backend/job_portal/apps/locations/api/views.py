from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAdminUser

from utils.permissions import HasSpecificPermission
from utils.pagination import CustomPagination
from ..models import Country, City
from .serializers import CountrySerializer, CitySerializer, CityListSerializer


class CountryAPIViewSet(viewsets.ModelViewSet):
    """ViewSet for managing countries."""

    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["is_deleted"]
    search_fields = ["name", "code"]
    ordering_fields = ["name", "code", "created_at"]
    ordering = ["name"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        else:
            return [
                IsAdminUser(),
                HasSpecificPermission(
                    ["locations.add_country", "locations.change_country", "locations.delete_country"]
                )()
            ]


class CityAPIViewSet(viewsets.ModelViewSet):
    """ViewSet for managing cities."""

    queryset = City.objects.select_related("country").all()
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["country", "is_deleted"]
    search_fields = ["name", "code", "country__name"]
    ordering_fields = ["name", "code", "created_at"]
    ordering = ["country__name", "name"]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return CityListSerializer
        else:
            return CitySerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        else:
            return [
                IsAdminUser(),
                HasSpecificPermission(
                    ["locations.add_city", "locations.change_city", "locations.delete_city"]
                )()
            ]


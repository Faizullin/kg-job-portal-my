from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api.views import CountryAPIViewSet, CityAPIViewSet

app_name = 'locations'

router = DefaultRouter()
router.register(r'api/v1/locations/countries', CountryAPIViewSet, basename='country')
router.register(r'api/v1/locations/cities', CityAPIViewSet, basename='city')

urlpatterns = [
    path('', include(router.urls)),
]
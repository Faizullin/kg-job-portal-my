from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api.views import (
    LanguageViewSet, ServiceCategoryViewSet, ServiceSubcategoryViewSet, 
    ServiceAreaViewSet, SystemSettingsViewSet, SupportFAQViewSet
)

app_name = 'core'

# Single router handles ALL endpoints
router = DefaultRouter()
router.register(r'languages', LanguageViewSet, basename='language')
router.register(r'service-categories', ServiceCategoryViewSet, basename='servicecategory')
router.register(r'service-subcategories', ServiceSubcategoryViewSet, basename='servicesubcategory')
router.register(r'service-areas', ServiceAreaViewSet, basename='servicearea')
router.register(r'system-settings', SystemSettingsViewSet, basename='systemsettings')
router.register(r'support/faq', SupportFAQViewSet, basename='supportfaq')

urlpatterns = [
    # All endpoints handled by router
    path('api/v1/core/', include(router.urls)),
]

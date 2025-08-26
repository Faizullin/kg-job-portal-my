from django.urls import path
from .api.views import (
    LanguageApiView, ServiceCategoryApiView, ServiceSubcategoryApiView,
    ServiceAreaApiView, SystemSettingsApiView, AppVersionApiView
)

app_name = 'core'

urlpatterns = [
    path('api/v1/core/languages/', LanguageApiView.as_view(), name='languages'),
    path('api/v1/core/service-categories/', ServiceCategoryApiView.as_view(), name='service-categories'),
    path('api/v1/core/service-subcategories/', ServiceSubcategoryApiView.as_view(), name='service-subcategories'),
    path('api/v1/core/service-areas/', ServiceAreaApiView.as_view(), name='service-areas'),
    path('api/v1/core/system-settings/', SystemSettingsApiView.as_view(), name='system-settings'),
    path('api/v1/core/app-versions/', AppVersionApiView.as_view(), name='app-versions'),
]

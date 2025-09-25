from django.urls import path
from .api.views import (
    GlobalSearchApiView, OrderSearchApiView, ProviderSearchApiView
)

app_name = 'search'

urlpatterns = [
    # Global search
    path('api/v1/search/global/', GlobalSearchApiView.as_view(), name='global-search'),
    path('api/v1/search/orders/', OrderSearchApiView.as_view(), name='order-search'),
    path('api/v1/search/providers/', ProviderSearchApiView.as_view(), name='provider-search'),
]

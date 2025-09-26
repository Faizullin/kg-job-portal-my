from django.urls import path
from .api.views import (
    ClientDashboardApiView, 
    # ProviderDashboardApiView,
    ServiceProviderSearchAPIView,
    OrderSearchAPIView
)

app_name = 'dashboard'

urlpatterns = [
    path('api/v1/dashboard/my/client/', ClientDashboardApiView.as_view(), name='client-dashboard'),
    # path('api/v1/dashboard/my/provider/', ProviderDashboardApiView.as_view(), name='provider-dashboard'),
    path('api/v1/search/providers/', ServiceProviderSearchAPIView.as_view(), name='provider-search'),
    path('api/v1/search/orders/', OrderSearchAPIView.as_view(), name='order-search'),
]

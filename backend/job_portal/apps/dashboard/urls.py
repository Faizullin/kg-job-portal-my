from django.urls import path
from .api.views import (
    ClientDashboardApiView, ProviderDashboardApiView
)

app_name = 'dashboard'

urlpatterns = [
    # Role-specific dashboard endpoints
    path('api/v1/dashboard/client/', ClientDashboardApiView.as_view(), name='client-dashboard'),
    path('api/v1/dashboard/provider/', ProviderDashboardApiView.as_view(), name='provider-dashboard'),
]

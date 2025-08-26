from django.urls import path
from .api.views import (
    UserProfileApiView, UserProfileDetailApiView, ServiceProviderApiView,
    ServiceProviderDetailApiView, ClientApiView, ClientDetailApiView
)

app_name = 'users'

urlpatterns = [
    # User Profiles
    path('api/v1/users/profiles/', UserProfileApiView.as_view(), name='profiles'),
    path('api/v1/users/profile/', UserProfileDetailApiView.as_view(), name='profile-detail'),
    
    # Service Providers
    path('api/v1/users/providers/', ServiceProviderApiView.as_view(), name='service-providers'),
    path('api/v1/users/provider/', ServiceProviderDetailApiView.as_view(), name='service-provider-detail'),
    
    # Clients
    path('api/v1/users/clients/', ClientApiView.as_view(), name='clients'),
    path('api/v1/users/client/', ClientDetailApiView.as_view(), name='client-detail'),
]

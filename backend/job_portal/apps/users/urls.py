from django.urls import path
from .api.views import (
    UserProfileApiView, UserProfileDetailApiView, ServiceProviderApiView,
    ServiceProviderDetailApiView, ClientApiView, ClientDetailApiView,
    UserProfileUpdateView, ClientProfileUpdateView, ServiceProviderProfileUpdateView
)

app_name = 'users'

urlpatterns = [
    # Profile Updates (works for both registration and profile updates)
    path('api/v1/users/profile/update/', UserProfileUpdateView.as_view(), name='profile-update'),
    path('api/v1/users/client/update/', ClientProfileUpdateView.as_view(), name='client-update'),
    path('api/v1/users/provider/update/', ServiceProviderProfileUpdateView.as_view(), name='provider-update'),
    
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

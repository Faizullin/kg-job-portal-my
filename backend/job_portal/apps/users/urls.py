from django.urls import path
from .api.views import (
    UserProfileDetailApiView, ServiceProviderApiView,
    ServiceProviderDetailApiView, ClientApiView, ClientDetailApiView,
    ClientProfileUpdateView, ServiceProviderProfileUpdateView,
    ClientProfileCreateView, ServiceProviderProfileCreateView,
    AdvancedProfileApiView, ServiceProviderFeaturedApiView, TaskHistoryApiView
)

app_name = 'users'

urlpatterns = [
    # Advanced Profile (combines user account + job portal profile)
    path('api/v1/users/profile/advanced/', AdvancedProfileApiView.as_view(), name='advanced-profile'),
    
    # Profile Creation (for initial setup)
    path('api/v1/users/client/create/', ClientProfileCreateView.as_view(), name='client-create'),
    path('api/v1/users/provider/create/', ServiceProviderProfileCreateView.as_view(), name='provider-create'),
    
    # User Profile (GET and UPDATE for current user)
    path('api/v1/users/profile/', UserProfileDetailApiView.as_view(), name='profile-detail'),
    
    # Profile Updates (for existing profiles)
    path('api/v1/users/client/update/', ClientProfileUpdateView.as_view(), name='client-update'),
    path('api/v1/users/provider/update/', ServiceProviderProfileUpdateView.as_view(), name='provider-update'),
    
    # Service Providers
    path('api/v1/users/providers/', ServiceProviderApiView.as_view(), name='service-providers'),
    path('api/v1/users/providers/featured/', ServiceProviderFeaturedApiView.as_view(), name='service-providers-featured'),
    path('api/v1/users/providers/<int:pk>/details/', ServiceProviderDetailApiView.as_view(), name='service-provider-details'),
    path('api/v1/users/provider/', ServiceProviderDetailApiView.as_view(), name='service-provider-detail'),
    
    # Clients
    path('api/v1/users/clients/', ClientApiView.as_view(), name='clients'),
    path('api/v1/users/client/', ClientDetailApiView.as_view(), name='client-detail'),
    
    # Task History
    path('api/v1/users/task-history/', TaskHistoryApiView.as_view(), name='task-history'),
]

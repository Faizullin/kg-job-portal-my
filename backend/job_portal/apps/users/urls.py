from django.urls import path
from .api.views import (
    UserProfileDetailApiView, ServiceProviderDetailApiView, 
    ClientProfileViewSet, ServiceProviderProfileViewSet,
    AdvancedProfileApiView,
    MasterSkillListApiView,
    ServiceProviderSkillApiView, PortfolioItemApiView, CertificateApiView,
    ProfessionListApiView, ProviderStatisticsApiView
)

app_name = 'users'

urlpatterns = [
    path('api/v1/users/my/profile/', UserProfileDetailApiView.as_view(), name='profile'),
    path('api/v1/users/my/profile/advanced/', AdvancedProfileApiView.as_view(), name='profile-advanced'),
    
    path('api/v1/users/my/client/', ClientProfileViewSet.as_view({
        "get": "retrieve",
        "post": "create",
        "put": "update",
        "patch": "partial_update",
    }), name='client-profile-viewset'),
    path('api/v1/users/my/provider/', ServiceProviderProfileViewSet.as_view({
        "get": "retrieve",
        "post": "create",
        "put": "update",
        "patch": "partial_update",
    }), name='provider-profile-viewset'),
    
    # Service Providers (Public - Detail Only)
    path('api/v1/users/providers/<int:pk>/details/', ServiceProviderDetailApiView.as_view(), name='provider-details'),
    
    # My Data Management
    path('api/v1/users/my/skills/', ServiceProviderSkillApiView.as_view(), name='my-skills'),
    path('api/v1/users/my/portfolio/', PortfolioItemApiView.as_view(), name='my-portfolio'),
    path('api/v1/users/my/certificates/', CertificateApiView.as_view(), name='my-certificates'),
    path('api/v1/users/my/statistics/', ProviderStatisticsApiView.as_view(), name='my-statistics'),
    
    # Reference Data (Public)
    path('api/v1/users/skills/', MasterSkillListApiView.as_view(), name='skills'),
    path('api/v1/users/professions/', ProfessionListApiView.as_view(), name='professions'),
]

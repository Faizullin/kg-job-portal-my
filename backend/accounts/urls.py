from django.urls import path
from .api.views import *

# Add app name for namespace
app_name = "accounts"


# URL patterns for accounts app
urlpatterns = [
    # Firebase authentication (replaces api_users auth endpoint)
    path('api/v1/auth/firebase/', FirebaseAuthView.as_view(), name='auth_firebase'),
    
    # User logout
    path('api/v1/auth/logout/', LogoutView.as_view(), name='auth_logout'),
    
    # User management endpoints (enhanced versions of api_users)
    path('api/v1/profile/', UserProfileApiView.as_view(), name='user_profile'),
    path('api/v1/users/', UserListApiView.as_view(), name='user_list'),
]
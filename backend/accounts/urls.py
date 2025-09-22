from django.urls import path
from .api.views import *

# Add app name for namespace
app_name = "accounts"


# URL patterns for accounts app
urlpatterns = [
    # Firebase authentication
    path('api/v1/auth/firebase/', FirebaseAuthView.as_view(), name='auth_firebase'),
    
    # Debug Firebase token endpoint (only works in DEBUG mode)
    path('api/v1/debug/firebase-token/', DebugFirebaseTokenView.as_view(), name='debug_firebase_token'),
    
    # User logout
    path('api/v1/auth/logout/', LogoutView.as_view(), name='auth_logout'),
    
    # User management endpoints
    path('api/v1/profile/', UserProfileApiView.as_view(), name='user_profile'),
    path('api/v1/users/', UserListApiView.as_view(), name='user_list'),
]
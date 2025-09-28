from django.urls import path

from .api.views import *

app_name = "accounts"

urlpatterns = [
    path('api/v1/auth/firebase/', FirebaseAuthView.as_view(), name='auth_firebase'),
    path('api/v1/auth/logout/', LogoutView.as_view(), name='auth_logout'),

    path('api/v1/profile/', UserProfileRetrieveUpdateAPIView.as_view(), name='user_profile'),
]

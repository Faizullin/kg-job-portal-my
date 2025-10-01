from django.urls import path

from .api.views import (
    FirebaseAuthView,
    LogoutView,
    UserProfileControlActionAPIView,
    UserProfileNotificationSettingsRetrieveUpdateAPIView,
    UserProfileRetrieveUpdateAPIView,
)

app_name = "accounts"

urlpatterns = [
    path("api/v1/auth/firebase/", FirebaseAuthView.as_view(), name="auth_firebase"),
    path("api/v1/auth/logout/", LogoutView.as_view(), name="auth_logout"),
    path(
        "api/v1/profile/",
        UserProfileRetrieveUpdateAPIView.as_view(),
        name="user_profile",
    ),
    path(
        "api/v1/profile/notification-settings/",
        UserProfileNotificationSettingsRetrieveUpdateAPIView.as_view(),
        name="user_profile_notification_settings",
    ),
    path(
        "api/v1/profile/control/",
        UserProfileControlActionAPIView.as_view(),
        name="user_profile_control",
    ),
]

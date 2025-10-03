from django.contrib.auth import get_user_model
from rest_framework.serializers import ValidationError
from django.core.files.storage import default_storage
from firebase_admin import auth
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from utils.views import ActionRequestException, BaseAction, BaseActionAPIView

from ...models import user_photo_storage_upload_to
from ..serializers import (
    UserDetailSerializer,
    UserNotificationSettingsSerializer,
    UserUpdateSerializer,
)

UserModel = get_user_model()


class UserProfileRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    """Retrieve or update authenticated user's profile, including profile image upload."""

    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == "GET":
            return UserDetailSerializer
        return UserUpdateSerializer


class UploadPhotoAction(BaseAction):
    name = "upload_photo"

    def apply(self, request):
        user = request.user
        if "photo" not in request.FILES:
            raise ValidationError("No photo file provided.")
        photo_file = request.FILES["photo"]
        if not photo_file.content_type.startswith("image/"):
            raise ValidationError("Uploaded file is not an image.")
        if photo_file.size > 5 * 1024 * 1024:  # 5MB limit
            raise ValidationError("Image file size exceeds the limit of 5MB.")

        file_path = user_photo_storage_upload_to(user, photo_file.name)
        saved_path = default_storage.save(file_path, photo_file)
        user.photo = saved_path
        user.photo_url = request.build_absolute_uri(user.photo.url) if user.photo else None
        user.save()

        return {
            "success": 1,
            "message": "Profile photo uploaded successfully.",
            "data": {"photo_url": user.photo_url},
        }


class RemovePhotoAction(BaseAction):
    name = "remove_photo"

    def apply(self, request):
        user = request.user
        use_reset = request.data.get("reset", False)
        if not user.photo:
            raise ValidationError("No profile photo to remove.")

        user.photo.delete(save=False)
        user.photo = None

        if use_reset:
            firebase_user_id = user.firebase_user_id
            if not firebase_user_id:
                raise ActionRequestException(
                    "Cannot reset to default photo without Firebase user ID."
                )
            initial_profile_photo_url = auth.get_user(firebase_user_id).photo_url
            user.photo_url = initial_profile_photo_url
        else:
            user.photo_url = request.build_absolute_uri(user.photo.url) if user.photo else None
        user.save()

        return {
            "success": 1,
            "message": "Profile photo removed successfully.",
            "data": {"photo_url": user.photo_url},
        }


class UserProfileControlActionAPIView(BaseActionAPIView):
    available_actions = [
        UploadPhotoAction(),
        RemovePhotoAction(),
    ]
    permission_classes = [IsAuthenticated]


class UserProfileNotificationSettingsRetrieveUpdateAPIView(
    generics.RetrieveUpdateAPIView
):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.notification_settings

    def get_serializer_class(self):
        return UserNotificationSettingsSerializer

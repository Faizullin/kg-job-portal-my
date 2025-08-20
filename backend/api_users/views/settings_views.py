from rest_framework.views import APIView
from rest_framework.request import Request

from api_users.serializers import *
from backend.global_function import error_with_text, success_with_text
from firebase_admin import auth


class EditPhotoView(APIView):
    def post(self, request: Request):
        data = request.data.dict()
        action_name = data.pop("action_name", None)
        if action_name is not None:
            if action_name == "reset":
                if not request.user.photo:
                    return error_with_text("No photo to reset")
                firebase_user_id = request.user.firebase_user_id
                firebase_user = auth.get_user(firebase_user_id)
                request.user.photo.delete()
                request.user.photo = None
                request.user.photo_url = firebase_user.photo_url
                request.user.save()
                return success_with_text("Photo deleted successfully")
            elif action_name != "upload":
                return error_with_text("Invalid action")
        if data.get("image", None) is not None:
            if request.user.photo:
                request.user.photo.delete()

            image_data = data.pop("image")
            request.user.photo = image_data
            request.user.save()

            return success_with_text(UserModelSerializer(request.user).data)
        return error_with_text("No image provided")


class EditUserSettingsView(APIView):
    def post(self, request: Request):
        serializer: EditUserSettingsSerializer = EditUserSettingsSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_with_text(UserModelSerializer(request.user).data)

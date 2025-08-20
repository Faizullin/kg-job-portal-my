from django.db import IntegrityError
from firebase_admin import auth
from firebase_admin._auth_utils import InvalidIdTokenError
from rest_framework.authtoken.models import Token
from rest_framework.request import Request
from rest_framework.views import APIView

from api_users.serializers import *
from backend.global_function import error_with_text, success_with_text


class AuthViaFirebase(APIView):
    serializer_class = FireBaseAuthSerializer
    permission_classes = []

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return error_with_text(serializer.errors)
        token = serializer.validated_data['token']

        # trying  to decode token, if not valid return error
        try:
            decoded_token = auth.verify_id_token(token)
        except ValueError:
            return error_with_text('The provided token is not a valid Firebase token')
        except InvalidIdTokenError:
            return error_with_text('The provided token is not a valid Firebase token')

        # trying to get the user id from the token, if not valid return error
        try:
            firebase_user_id = decoded_token['uid']
        except KeyError:
            return error_with_text('The user provided with the auth token is not a valid '
                                   'Firebase user, it has no Firebase UID')

        # trying to get the user from the database, if not found create a new user
        try:
            user_profile = UserModel.objects.get(firebase_user_id=firebase_user_id)
        except UserModel.DoesNotExist:
            firebase_user = auth.get_user(firebase_user_id)
            try:
                user_profile: UserModel = UserModel.objects.create(
                    photo_url=firebase_user.photo_url,
                    name=firebase_user.display_name.split()[0],
                    email=firebase_user.email,
                    firebase_user_id=firebase_user_id,
                    description='no bio yet',
                    username=firebase_user.email,
                    password='no password',
                )
                user_profile.set_password('no password')
                user_profile.save()
                NotificationSettings.objects.create(user=user_profile)


            except IntegrityError as e:
                print(e)
                return error_with_text('A user with the provided Firebase UID already exists')

        # delete old token and generate a new one
        Token.objects.filter(user=user_profile).delete()
        token = Token.objects.create(user=user_profile)
        return success_with_text(UserModelSerializer(user_profile).data | {'token': token.key})

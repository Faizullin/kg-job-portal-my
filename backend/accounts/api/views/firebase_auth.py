from django.db import IntegrityError
from firebase_admin import auth
from firebase_admin._auth_utils import InvalidIdTokenError
from rest_framework.authtoken.models import Token
from rest_framework.request import Request
from rest_framework.views import APIView
from django.utils import timezone

from ...models import UserModel, NotificationSettings
from ..serializers import FireBaseAuthSerializer
from backend.global_function import error_with_text, success_with_text


class FirebaseAuthView(APIView):
    """Firebase authentication view - replaces api_users AuthViaFirebase"""
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
            user_profile = UserModel.objects.get(firebase_user_id=firebase_user_id, is_deleted=False)
        except UserModel.DoesNotExist:
            # Check if user exists but is deleted
            try:
                deleted_user = UserModel.objects.get(firebase_user_id=firebase_user_id, is_deleted=True)
                # Restore the deleted user
                deleted_user.restore()
                user_profile = deleted_user
            except UserModel.DoesNotExist:
                # Create new user
                firebase_user = auth.get_user(firebase_user_id)
                try:
                    user_profile: UserModel = UserModel.objects.create(
                        photo_url=firebase_user.photo_url,
                        name=firebase_user.display_name.split()[0] if firebase_user.display_name else 'User',
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

        # Check if user is blocked
        if user_profile.blocked:
            return error_with_text('User account is blocked')

        # Check if user is active
        if not user_profile.is_active:
            return error_with_text('User account is disabled')

        # delete old token and generate a new one
        Token.objects.filter(user=user_profile).delete()
        token = Token.objects.create(user=user_profile)
        
        # Create login session for tracking
        from ...models import LoginSession
        LoginSession.objects.create(
            user=user_profile,
            session_key=token.key,
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return success_with_text({
            'token': token.key,
            'user': {
                'id': user_profile.id,
                'username': user_profile.username,
                'email': user_profile.email,
                'name': user_profile.name,
                'description': user_profile.description,
                'photo_url': user_profile.photo_url,
                'user_type': user_profile.user_type,
                'timezone_difference': user_profile.timezone_difference,
                'points': user_profile.points,
                'day_streak': user_profile.day_streak,
                'max_day_streak': user_profile.max_day_streak,
            }
        })
    
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

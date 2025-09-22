from django.db import IntegrityError
from django.conf import settings
from firebase_admin import auth
from firebase_admin.auth import InvalidIdTokenError
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.helpers import get_client_ip
from ..serializers import FireBaseAuthSerializer, FirebaseAuthResponseSerializer, UserProfileSerializer
from ...models import UserModel




class FirebaseAuthView(APIView):
    """Firebase authentication view - replaces api_users AuthViaFirebase"""
    serializer_class = FireBaseAuthSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """Authenticate user with Firebase ID token or register new user if verified."""
        id_token = request.data.get('id_token')

        if not id_token:
            return Response({'error': 'id_token is required'}, status=400)

        try:
            # Verify Firebase ID token
            try:
                decoded_token = auth.verify_id_token(id_token)
                firebase_user_id = decoded_token['uid']
                firebase_user = auth.get_user(firebase_user_id)

            except InvalidIdTokenError:
                return Response({'error': 'Invalid Firebase ID token'}, status=400)
            except Exception as firebase_error:
                return Response({'error': f'Firebase verification failed: {str(firebase_error)}'}, status=400)

            # Try to get active user first (manager automatically filters deleted users)
            try:
                user_profile = UserModel.objects.get(firebase_user_id=firebase_user_id)

                # Check if user is active
                if not user_profile.is_active:
                    return Response({'error': 'User account is deactivated'}, status=403)

                # Generate or get existing token
                token, created = Token.objects.get_or_create(user=user_profile)

                # Use UserProfileSerializer for consistent response
                user_serializer = UserProfileSerializer(user_profile)
                response_data = {
                    'token': token.key,
                    'user': user_serializer.data,
                    'message': 'Authentication successful'
                }

                # Serialize the response for OpenAPI documentation
                serializer = FirebaseAuthResponseSerializer(response_data)
                return Response(serializer.data)

            except UserModel.DoesNotExist:
                # Check if user was soft-deleted
                try:
                    # Use all_with_deleted to check for deleted users
                    deleted_user = UserModel.objects.all_with_deleted().get(firebase_user_id=firebase_user_id)
                    if deleted_user.is_deleted:
                        return Response({
                            'error': 'User account has been deleted',
                            'deleted_at': deleted_user.deleted_at
                        }, status=410)
                except UserModel.DoesNotExist:
                    pass

                # User doesn't exist - create new user from Firebase data
                # Firebase user is already verified above
                user_profile = self._create_user_from_firebase(firebase_user)

                # Generate token for new user
                token, created = Token.objects.get_or_create(user=user_profile)

                # Use UserProfileSerializer for consistent response
                user_serializer = UserProfileSerializer(user_profile)
                response_data = {
                    'token': token.key,
                    'user': user_serializer.data,
                    'message': 'User registered and authenticated successfully'
                }

                # Serialize the response for OpenAPI documentation
                serializer = FirebaseAuthResponseSerializer(response_data)
                return Response(serializer.data, status=201)

        except Exception as e:
            return Response({'error': str(e)}, status=500)

    def _create_user_from_firebase(self, firebase_user):
        """Create a new user from Firebase user data."""
        try:
            # Extract user data from Firebase
            email = firebase_user.email or ''
            display_name = firebase_user.display_name or ''
            photo_url = firebase_user.photo_url or ''

            # Generate username from email or display name
            if email:
                username = email.split('@')[0]
            else:
                username = display_name.replace(' ', '_').lower() if display_name else f'user_{firebase_user.uid[:8]}'

            # Ensure username is unique
            base_username = username
            counter = 1
            while UserModel.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1

            # Create new user
            user_profile = UserModel.objects.create(
                firebase_user_id=firebase_user.uid,
                username=username,
                email=email,
                name=display_name,
                photo_url=photo_url,
                is_active=True,
                user_type='free',  # Default user type
            )

            # Automatically create UserProfile for job portal
            from job_portal.apps.users.models import UserProfile
            UserProfile.objects.create(
                user=user_profile,
                user_type='client',  # Default to client
                is_verified=False,
            )

            return user_profile

        except IntegrityError as e:
            # Handle case where user might already exist (race condition)
            try:
                return UserModel.objects.get(firebase_user_id=firebase_user.uid)
            except UserModel.DoesNotExist:
                raise e

    def _get_client_ip(self, request):
        return get_client_ip(request)


class DebugFirebaseTokenView(APIView):
    """Debug view to get Firebase user token by email - only available in DEBUG mode"""
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        """Get Firebase user token by email address - DEBUG ONLY"""
        # Only allow in DEBUG mode
        if not settings.DEBUG:
            return Response({'error': 'This endpoint is only available in DEBUG mode'}, status=403)
        
        email = request.data.get('email')
        if not email:
            return Response({'error': 'email is required'}, status=400)
        
        try:
            # Get user by email from Firebase
            firebase_user = auth.get_user_by_email(email)
            
            # Create custom token for this user
            custom_token = auth.create_custom_token(firebase_user.uid)
            
            response_data = {
                'firebase_user_id': firebase_user.uid,
                'email': firebase_user.email,
                'display_name': firebase_user.display_name,
                'photo_url': firebase_user.photo_url,
                'custom_token': custom_token.decode('utf-8'),
                'user_metadata': {
                    'creation_timestamp': firebase_user.user_metadata.creation_timestamp,
                    'last_sign_in_timestamp': firebase_user.user_metadata.last_sign_in_timestamp,
                },
                'provider_data': [
                    {
                        'provider_id': provider.provider_id,
                        'uid': provider.uid,
                        'email': provider.email,
                        'display_name': provider.display_name,
                        'photo_url': provider.photo_url,
                    }
                    for provider in firebase_user.provider_data
                ]
            }
            
            return Response(response_data)
            
        except auth.UserNotFoundError:
            return Response({'error': f'User with email {email} not found in Firebase'}, status=404)
        except Exception as e:
            return Response({'error': f'Error getting Firebase user: {str(e)}'}, status=500)

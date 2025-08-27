from utils.helpers import get_client_ip
from django.db import IntegrityError
from firebase_admin import auth
from firebase_admin._auth_utils import InvalidIdTokenError
from rest_framework.authtoken.models import Token
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

from ...models import UserModel, NotificationSettings
from ..serializers import FireBaseAuthSerializer
# Utility functions replaced with direct Response objects


class FirebaseAuthView(APIView):
    """Firebase authentication view - replaces api_users AuthViaFirebase"""
    serializer_class = FireBaseAuthSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        """Authenticate user with Firebase token."""
        firebase_user_id = request.data.get('firebase_user_id')
        
        if not firebase_user_id:
            return Response({'error': 'firebase_user_id is required'}, status=400)
        
        try:
            # Try to get active user first (manager automatically filters deleted users)
            user_profile = UserModel.objects.get(firebase_user_id=firebase_user_id)
            
            # Check if user is active
            if not user_profile.is_active:
                return Response({'error': 'User account is deactivated'}, status=403)
            
            # Generate or get existing token
            token, created = Token.objects.get_or_create(user=user_profile)
            
            return Response({
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
                },
                'message': 'Authentication successful'
            })
            
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
            
            return Response({'error': 'User not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
    
    def _get_client_ip(self, request):
        return get_client_ip(request)
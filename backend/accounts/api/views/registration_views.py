from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token

from ...models import UserModel, UserRoleTypes
from ..serializers import UserRegistrationSerializer, UserProfileSerializer


class UserRegistrationView(APIView):
    """Simple user registration after Firebase authentication"""
    permission_classes = [AllowAny]

    def post(self, request):
        """Complete user registration with role and service categories"""
        serializer = UserRegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user already exists
        email = serializer.validated_data['email']
        if UserModel.objects.filter(email=email).exists():
            return Response({
                'error': 'User with this email already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create user
        try:
            user = UserModel.objects.create(
                email=email,
                name=serializer.validated_data['name'],
                phone_number=serializer.validated_data.get('phone_number'),
                user_role=serializer.validated_data.get('user_role'),
                service_categories=serializer.validated_data.get('service_categories', []),
                description=serializer.validated_data.get('description', ''),
                photo_url=serializer.validated_data.get('photo_url'),
                is_active=True,
                user_type='free'
            )
            
            # Generate username
            base_username = email.split('@')[0]
            username = base_username
            counter = 1
            while UserModel.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
            
            user.username = username
            user.save()
            
            # Generate token
            token, created = Token.objects.get_or_create(user=user)
            
            # Return user profile
            user_serializer = UserProfileSerializer(user)
            return Response({
                'message': 'Registration completed successfully',
                'token': token.key,
                'user': user_serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': 'Registration failed. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

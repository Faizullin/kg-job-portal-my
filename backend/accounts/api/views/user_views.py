from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.files.storage import default_storage
import uuid

from ...models import UserModel
from ..serializers import (
    UserListSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
)
from utils.pagination import CustomPagination


class UserProfileApiView(generics.RetrieveUpdateAPIView):
    """User profile view with image upload"""
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserProfileSerializer
        return UserUpdateSerializer
    
    def post(self, request):
        """Upload profile image"""
        if 'photo' not in request.FILES:
            return Response({
                'message': 'No image file provided',
                'errors': {'photo': ['This field is required.']}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        image_file = request.FILES['photo']
        
        # Basic validation
        if image_file.size > 5 * 1024 * 1024:  # 5MB limit
            return Response({
                'message': 'File too large',
                'errors': {'photo': ['File size must be no more than 5MB.']}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check file type
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if hasattr(image_file, 'content_type') and image_file.content_type not in allowed_types:
            return Response({
                'message': 'Invalid file type',
                'errors': {'photo': ['Only JPEG, PNG, GIF and WebP images are allowed.']}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Delete old image if exists
            if request.user.photo:
                if default_storage.exists(request.user.photo.name):
                    default_storage.delete(request.user.photo.name)
            
            # Generate unique filename
            unique_id = uuid.uuid4().hex[:8]
            filename = f"user_photos/{request.user.id}/profile_{unique_id}.jpg"
            
            # Save the image
            request.user.photo.save(filename, image_file, save=True)
            
            # Return success response
            image_url = request.build_absolute_uri(request.user.photo.url) if request.user.photo else None
            
            return Response({
                'message': 'Profile image uploaded successfully',
                'image_url': image_url
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'message': 'Failed to upload image',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        """Reset profile image to default by removing uploaded photo.

        This clears the stored ImageField `photo`. The `photo_url` (e.g., Firebase avatar)
        remains unchanged. Frontend should use `photo_url` as fallback.
        """
        try:
            # Delete stored image file if exists
            if request.user.photo:
                try:
                    if default_storage.exists(request.user.photo.name):
                        default_storage.delete(request.user.photo.name)
                except Exception:
                    # Ignore storage errors during delete; proceed to clear field
                    pass
                request.user.photo.delete(save=False)

            # Clear reference and save
            request.user.photo = None
            request.user.save(update_fields=["photo"]) 

            image_url = request.build_absolute_uri(request.user.photo.url) if request.user.photo else None
            return Response({
                'message': 'Profile image reset successfully',
                'image_url': image_url,
                'photo_url': request.user.photo_url,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'message': 'Failed to reset image',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserListApiView(generics.ListAPIView):
    """List all users - not in api_users, useful for admin"""
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user_type', 'is_active', 'blocked']
    search_fields = ['username', 'email', 'name']
    ordering_fields = ['date_joined', 'username', 'name']
    ordering = ['-date_joined']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        # Manager automatically filters out deleted objects
        return UserModel.objects.filter(is_active=True).order_by('-date_joined')

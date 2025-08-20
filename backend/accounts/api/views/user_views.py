from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from ...models import UserModel
from ..serializers import UserProfileSerializer, UserUpdateSerializer, UserListSerializer
from ..permissions import IsOwnerOrStaff, HasPermission


class UserProfileApiView(generics.RetrieveUpdateAPIView):
    """User profile view - enhanced version of api_users GetUserView"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class UserListApiView(generics.ListAPIView):
    """List all users - not in api_users, useful for admin"""
    serializer_class = UserListSerializer
    permission_classes = [HasPermission('auth.view_user')]
    queryset = UserModel.objects.filter(is_active=True, is_deleted=False).order_by('-date_joined')
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by search query
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                username__icontains=search
            ) | queryset.filter(
                email__icontains=search
            ) | queryset.filter(
                first_name__icontains=search
            ) | queryset.filter(
                last_name__icontains=search
            )
        
        # Filter by group
        group = self.request.query_params.get('group', None)
        if group:
            queryset = queryset.filter(groups__name=group)
        
        # Filter by status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by delete status
        show_deleted = self.request.query_params.get('show_deleted', 'false').lower() == 'true'
        if show_deleted:
            queryset = UserModel.objects.filter(is_active=True).order_by('-date_joined')
        
        return queryset.distinct()


class UserUpdateApiView(generics.UpdateAPIView):
    """Update user - enhanced version of api_users EditUserSettingsView"""
    serializer_class = UserUpdateSerializer
    permission_classes = [IsOwnerOrStaff]
    queryset = UserModel.objects.filter(is_deleted=False)


# Individual user detail view
class UserDetailApiView(generics.RetrieveAPIView):
    """Get detailed user information - not in api_users, useful for admin"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsOwnerOrStaff]
    queryset = UserModel.objects.filter(is_deleted=False)

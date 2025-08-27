from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import StandardResultsSetPagination

from ...models import UserModel
from ..serializers import UserProfileSerializer, UserUpdateSerializer, UserListSerializer, UserDetailSerializer
from ..permissions import AbstractIsAuthenticatedOrReadOnly


class UserProfileApiView(generics.RetrieveUpdateAPIView):
    """User profile view - enhanced version of api_users GetUserView"""
    serializer_class = UserProfileSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    
    def get_object(self):
        return self.request.user


class UserListApiView(generics.ListAPIView):
    """List all users - not in api_users, useful for admin"""
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user_type', 'is_active', 'blocked']
    search_fields = ['username', 'email', 'name']
    ordering_fields = ['date_joined', 'username', 'name']
    ordering = ['-date_joined']
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        # Manager automatically filters out deleted objects
        return UserModel.objects.filter(is_active=True).order_by('-date_joined')
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserListSerializer
        return UserUpdateSerializer


class UserUpdateApiView(generics.UpdateAPIView):
    """Update user - enhanced version of api_users EditUserSettingsView"""
    serializer_class = UserUpdateSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    queryset = UserModel.objects.filter(is_deleted=False)


# Individual user detail view
class UserDetailApiView(generics.RetrieveUpdateAPIView):
    """Get detailed user information - not in api_users, useful for admin"""
    serializer_class = UserDetailSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        # Manager automatically filters out deleted objects
        return UserModel.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserDetailSerializer
        return UserUpdateSerializer

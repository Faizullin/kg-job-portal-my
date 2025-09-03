from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import OrderingFilter, SearchFilter
from utils.pagination import CustomPagination
from rest_framework.permissions import IsAuthenticated

from ...models import UserModel
from utils.permissions import AbstractIsAuthenticatedOrReadOnly
from ..serializers import (
    UserListSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
)


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
    pagination_class = CustomPagination
    
    def get_queryset(self):
        # Manager automatically filters out deleted objects
        return UserModel.objects.filter(is_active=True).order_by('-date_joined')
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserListSerializer
        return UserUpdateSerializer

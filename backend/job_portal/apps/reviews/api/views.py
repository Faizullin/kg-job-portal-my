from rest_framework import generics
from rest_framework.response import Response
from django.db.models import Avg, Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from utils.permissions import AbstractIsAuthenticatedOrReadOnly
from utils.pagination import CustomPagination
from ..models import Review
from .serializers import ReviewSerializer, ReviewCreateSerializer, ReviewUpdateSerializer, ReviewAnalyticsSerializer


class ReviewApiView(generics.ListCreateAPIView):
    """List and create reviews."""
    serializer_class = ReviewSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['overall_rating', 'is_verified']
    search_fields = ['title', 'comment', 'reviewer__name', 'provider__user_profile__user__name']
    ordering_fields = ['overall_rating', 'created_at']
    ordering = ['-created_at']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        return Review.objects.filter(
            is_deleted=False
        ).select_related(
            'reviewer', 
            'provider__user_profile__user',
            'order'
        )
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ReviewCreateSerializer
        return ReviewSerializer
    
    def perform_create(self, serializer):
        # Set the reviewer to the current user
        serializer.save(reviewer=self.request.user)


class ReviewDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete specific review."""
    serializer_class = ReviewUpdateSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return Review.objects.filter(
            is_deleted=False
        ).select_related(
            'reviewer', 
            'provider__user_profile__user',
            'order'
        )
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ReviewSerializer
        return ReviewUpdateSerializer


class ProviderReviewsApiView(generics.ListAPIView):
    """Get reviews for a specific service provider."""
    serializer_class = ReviewSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['overall_rating', 'is_verified']
    ordering_fields = ['overall_rating', 'created_at']
    ordering = ['-created_at']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        provider_id = self.kwargs.get('provider_id')
        return Review.objects.filter(
            provider_id=provider_id,
            is_deleted=False
        ).select_related(
            'reviewer', 
            'provider__user_profile__user',
            'order'
        )


class OrderReviewsApiView(generics.ListAPIView):
    """Get reviews for a specific order."""
    serializer_class = ReviewSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination
    
    def get_queryset(self):
        order_id = self.kwargs.get('order_id')
        return Review.objects.filter(
            order_id=order_id,
            is_deleted=False
        ).select_related(
            'reviewer', 
            'provider__user_profile__user',
            'order'
        )


class ReviewAnalyticsApiView(generics.GenericAPIView):
    """Get simple review analytics for a provider."""
    serializer_class = ReviewAnalyticsSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        provider_id = self.kwargs.get('provider_id')
        return Review.objects.filter(
            provider_id=provider_id,
            is_deleted=False
        ).select_related(
            'reviewer', 
            'provider__user_profile__user',
            'order'
        )
    
    def get(self, request, *args, **kwargs):
        """Get review analytics."""
        provider_id = self.kwargs.get('provider_id')
        
        # Get basic stats
        reviews = Review.objects.filter(
            provider_id=provider_id,
            is_deleted=False
        )
        
        total_reviews = reviews.count()
        avg_rating = reviews.aggregate(avg_rating=Avg('overall_rating'))['avg_rating'] or 0
        
        # Rating distribution
        rating_distribution = reviews.values('overall_rating').annotate(
            count=Count('id')
        ).order_by('overall_rating')
        
        stats = {
            'total_reviews': total_reviews,
            'average_rating': round(avg_rating, 2),
            'rating_distribution': list(rating_distribution)
        }
        
        serializer = self.get_serializer(stats)
        return Response(serializer.data)


from rest_framework import generics, status
from rest_framework.response import Response
from django.db import models
from django.db.models import Avg, Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse

from rest_framework.permissions import IsAuthenticated
from utils.exceptions import StandardizedViewMixin
from utils.pagination import CustomPagination
from ..models import Review
from .serializers import (
    ReviewSerializer, ReviewCreateSerializer, ReviewUpdateSerializer, 
    ReviewAnalyticsSerializer, ClientRatingSerializer, OrderAssignmentReviewSerializer
)


@extend_schema_view(
    get=extend_schema(
        summary="List reviews",
        description="Get a list of all reviews with filtering and search capabilities",
        responses={
            200: ReviewSerializer(many=True),
            401: OpenApiResponse(description="Authentication required"),
        }
    ),
    post=extend_schema(
        summary="Create review",
        description="Create a new review for a completed order",
        request=ReviewCreateSerializer,
        responses={
            201: ReviewSerializer,
            400: OpenApiResponse(description="Invalid data"),
            401: OpenApiResponse(description="Authentication required"),
        }
    )
)
class ReviewApiView(StandardizedViewMixin, generics.ListCreateAPIView):
    """List and create reviews with OpenAPI documentation."""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['overall_rating', 'is_verified']
    search_fields = ['title', 'comment', 'reviewer__first_name', 'provider__user_profile__user__first_name']
    ordering_fields = ['overall_rating', 'created_at']
    ordering = ['-created_at']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        return Review.objects.select_related(
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


class ReviewDetailApiView(StandardizedViewMixin, generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete specific review."""
    serializer_class = ReviewUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Review.objects.select_related(
            'reviewer', 
            'provider__user_profile',
            'order'
        )
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ReviewSerializer
        return ReviewUpdateSerializer


class ProviderReviewsApiView(StandardizedViewMixin, generics.ListAPIView):
    """Get reviews for a specific service provider."""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['overall_rating', 'is_verified']
    ordering_fields = ['overall_rating', 'created_at']
    ordering = ['-created_at']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        provider_id = self.kwargs.get('provider_id')
        return Review.objects.filter(
            provider_id=provider_id
        ).select_related(
            'reviewer', 
            'provider__user_profile',
            'order'
        )


class OrderReviewsApiView(StandardizedViewMixin, generics.ListAPIView):
    """Get reviews for a specific order."""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    
    def get_queryset(self):
        order_id = self.kwargs.get('order_id')
        return Review.objects.filter(
            order_id=order_id,
        ).select_related(
            'reviewer', 
            'provider__user_profile',
            'order'
        )


class ReviewAnalyticsApiView(StandardizedViewMixin, generics.GenericAPIView):
    """Get simple review analytics for a provider."""
    serializer_class = ReviewAnalyticsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        provider_id = self.kwargs.get('provider_id')
        return Review.objects.filter(
            provider_id=provider_id
        ).select_related(
            'reviewer', 
            'provider__user_profile',
            'order'
        )
    
    def get(self, request, *args, **kwargs):
        """Get review analytics."""
        provider_id = self.kwargs.get('provider_id')
        
        # Get basic stats
        reviews = Review.objects.filter(
            provider_id=provider_id
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


@extend_schema_view(
    get=extend_schema(
        summary="Get order assignment reviews",
        description="Get review data from order assignments (client ratings)",
        responses={
            200: OrderAssignmentReviewSerializer(many=True),
            401: OpenApiResponse(description="Authentication required"),
        }
    )
)
class OrderAssignmentReviewsApiView(StandardizedViewMixin, generics.ListAPIView):
    """Get review data from order assignments."""
    serializer_class = OrderAssignmentReviewSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    
    def get_queryset(self):
        """Get order assignments with review data."""
        from job_portal.apps.orders.models import OrderAssignment
        
        user = self.request.user
        
        # Get assignments where user is either client or provider
        assignments = OrderAssignment.objects.filter(
            models.Q(order__client__user_profile__user=user) |
            models.Q(provider__user_profile__user=user)
        ).select_related(
            'order__client__user_profile__user',
            'provider__user_profile__user'
        )
        
        return assignments
    
    def list(self, request, *args, **kwargs):
        """Return serialized assignment review data."""
        assignments = self.get_queryset()
        
        review_data = []
        for assignment in assignments:
            data = {
                'order_id': assignment.order.id,
                'order_title': assignment.order.title,
                'provider_name': assignment.provider.user_profile.user.get_full_name() or assignment.provider.user_profile.user.username,
                'client_name': assignment.order.client.user_profile.user.get_full_name() or assignment.order.client.user_profile.user.username,
                'client_rating': assignment.client_rating,
                'client_review': assignment.client_review,
                'provider_rating': None,  # This would come from Review model
                'provider_review': None,  # This would come from Review model
                'completed_at': assignment.order.completed_at
            }
            
            # Get provider review if exists
            try:
                provider_review = Review.objects.get(
                    order=assignment.order,
                    reviewer=assignment.provider.user_profile.user
                )
                data['provider_rating'] = provider_review.overall_rating
                data['provider_review'] = provider_review.comment
            except Review.DoesNotExist:
                pass
            
            review_data.append(data)
        
        serializer = self.get_serializer(review_data, many=True)
        return Response(serializer.data)




from utils.permissions import HasSpecificPermission
from django.db import models
from django.db.models import Avg, Count
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.decorators import action
from job_portal.apps.users.models import Master
from rest_framework.generics import get_object_or_404
from job_portal.apps.jobs.models import Job

from utils.pagination import CustomPagination
from .serializers import (
    ReviewSerializer, ReviewCreateSerializer, ReviewUpdateSerializer,
    ReviewAnalyticsSerializer, JobAssignmentReviewSerializer
)
from ..models import Review


class ReviewAPIViewSet(ReadOnlyModelViewSet):
    """Comprehensive review management with additional actions."""
    
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['rating', 'is_verified', 'master', 'job']
    search_fields = ['title', 'comment', 'reviewer__first_name', 'master__user__first_name']
    ordering_fields = ['rating', 'created_at']
    ordering = ['-created_at']
    pagination_class = CustomPagination

    def get_queryset(self):
        return Review.objects.select_related(
            'reviewer',
            'master__user',
            'job'
        )
    
    def get_permissions(self):
        perms = super().get_permissions()
        return perms

    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ReviewUpdateSerializer
        return ReviewSerializer

    def perform_create(self, serializer):
        """Set the reviewer to the current user."""
        serializer.save(reviewer=self.request.user)

    @extend_schema(
        description="Get all reviews for a specific master",
        responses={200: ReviewSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='master/(?P<master_id>[^/.]+)')
    def master_reviews(self, request, master_id=None):
        """Get reviews for a specific master."""
        master = get_object_or_404(Master, id=master_id)
        reviews = self.get_queryset().filter(master=master)
        
        # Apply filtering and pagination
        reviews = self.filter_queryset(reviews)
        page = self.paginate_queryset(reviews)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)

    @extend_schema(
        description="Get all reviews for a specific job",
        responses={200: ReviewSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='job/(?P<job_id>[^/.]+)')
    def job_reviews(self, request, job_id=None):
        """Get reviews for a specific job."""
        job = get_object_or_404(Job, id=job_id)
        reviews = self.get_queryset().filter(job=job)
        
        # Apply filtering and pagination
        reviews = self.filter_queryset(reviews)
        page = self.paginate_queryset(reviews)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)

    @extend_schema(
        description="Get review analytics for a specific master",
        responses={200: ReviewAnalyticsSerializer}
    )
    @action(detail=False, methods=['get'], url_path='analytics/(?P<master_id>[^/.]+)')
    def analytics(self, request, master_id=None):
        """Get review analytics for a specific master."""
        master = get_object_or_404(Master, id=master_id)
        reviews = Review.objects.filter(master=master)
        
        total_reviews = reviews.count()
        avg_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
        
        # Rating distribution
        rating_distribution = reviews.values('rating').annotate(
            count=Count('id')
        ).order_by('rating')
        
        stats = {
            'total_reviews': total_reviews,
            'average_rating': round(avg_rating, 2),
            'rating_distribution': list(rating_distribution)
        }
        
        serializer = ReviewAnalyticsSerializer(stats)
        return Response(serializer.data)

    @extend_schema(
        description="Get review data from job assignments",
        responses={200: JobAssignmentReviewSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def assignments(self, request):
        """Get review data from job assignments."""
        from job_portal.apps.jobs.models import JobAssignment
        
        user = request.user
        
        # Get assignments where user is either client or master
        assignments = JobAssignment.objects.filter(
            models.Q(job__employer__user=user) |
            models.Q(master__user=user)
        ).select_related(
            'job__employer__user',
            'master__user'
        )
        
        review_data = []
        for assignment in assignments:
            data = {
                'job_id': assignment.job.id,
                'job_title': assignment.job.title,
                'master_name': assignment.master.user.get_full_name() or assignment.master.user.username,
                'client_name': assignment.job.employer.user.get_full_name() or assignment.job.employer.user.username,
                'client_rating': assignment.client_rating,
                'client_review': assignment.client_review,
                'master_rating': None,
                'master_review': None,
                'completed_at': assignment.job.completed_at
            }
            
            # Get master review if exists
            try:
                master_review = Review.objects.get(
                    job=assignment.job,
                    reviewer=assignment.master.user
                )
                data['master_rating'] = master_review.rating
                data['master_review'] = master_review.comment
            except Review.DoesNotExist:
                pass
            
            review_data.append(data)
        
        serializer = JobAssignmentReviewSerializer(review_data, many=True)
        return Response(serializer.data)

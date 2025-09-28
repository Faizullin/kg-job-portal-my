from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from job_portal.apps.notifications.models import notify
from job_portal.apps.users.api.permissions import HasEmployerProfile, HasMasterProfile
from utils.permissions import (
    HasSpecificPermission,
)
from .filters import JobApplicationFilter
from .permissions import JobAccessPermission
from .serializers import (
    CResponseSerializer,
    JobApplicationSerializer,
    JobApplySerializer,
    JobAssignmentSerializer,
    JobSerializer,
    ProgressUpdateSerializer,
    RatingSerializer,
)
from ..models import (
    Job,
    JobApplication,
    JobApplicationStatus,
    JobAssignment,
    JobAssignmentStatus,
    JobStatus,
    BookmarkJob,
    FavoriteJob,
)
from ...chats.models import ChatRoom, ChatParticipant, ChatRole


class _JobApiActionSerializer(CResponseSerializer):
    data = JobSerializer(read_only=True)


class JobAPIViewSet(ModelViewSet):
    """ViewSet for managing jobs."""

    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = JobSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "service_subcategory", "urgency"]
    search_fields = ["title", "description", "special_requirements"]
    ordering_fields = [
        "created_at",
        "budget_min",
        "budget_max",
    ]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = Job.objects.all().select_related("employer__user", "service_subcategory")
        user = self.request.user
        has_edit_access = user.is_authenticated and hasattr(user, "employer_profile")
        if has_edit_access:
            qs = qs.filter(employer=user.employer_profile)
        else:
            qs = qs.filter(status=JobStatus.PUBLISHED)
        return qs

    def get_permissions(self):
        perms = super().get_permissions()
        if self.action == "list":
            pass
        elif self.action == "retrieve":
            perms.append(JobAccessPermission)
        elif self.action in [
            "update",
            "partial_update",
            "destroy",
            "publish",
            "cancel",
        ]:
            perms.append(HasSpecificPermission(["jobs.change_job"]))
            perms.append(JobAccessPermission)
        elif self.action == "create":
            perms.append(HasSpecificPermission(["jobs.add_job"]))
        elif self.action == "apply":
            perms += [
                IsAuthenticated,
                HasMasterProfile,
                HasSpecificPermission(["jobs.add_jobapplication"]),
            ]
        return perms

    @extend_schema(
        description="Publish a draft job. Only allowed if job is in DRAFT state.",
        responses={
            200: _JobApiActionSerializer,
        },
    )
    @action(detail=True, methods=["post"])
    def publish(self, request):
        job = self.get_object()
        if job.status != JobStatus.DRAFT:
            raise ValidationError("Job cannot be published in its current state.")
        job.status = JobStatus.PUBLISHED
        job.published_at = timezone.now()
        job.save()
        return Response(
            {
                "message": "Job published successfully",
                "data": _JobApiActionSerializer(job).data,
            }
        )

    @extend_schema(
        description="Cancel a job. Only allowed if job is in PUBLISHED or ASSIGNED state.",
        responses={
            200: _JobApiActionSerializer,
        },
    )
    @action(detail=True, methods=["post"])
    def cancel(self, request):
        job = self.get_object()
        if job.status not in [JobStatus.PUBLISHED, JobStatus.ASSIGNED]:
            raise ValidationError("Job cannot be cancelled in its current state.")

        job.status = JobStatus.CANCELLED
        job.cancelled_at = timezone.now()
        job.save()
        return Response(
            {
                "message": "Job cancelled successfully",
                "data": JobSerializer(job).data,
            }
        )

    @extend_schema(
        description="Apply to a job.",
        request=JobApplySerializer,
        responses={
            200: _JobApiActionSerializer,
        },
    )
    @action(detail=True, methods=["post"])
    def apply(self, request, *args, **kwargs):
        job = self.get_object()
        serializer = JobApplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        master_profile = request.user.master_profile
        existing_job_application = JobApplication.objects.filter(
            job=job,
            applicant=master_profile,
        )
        if existing_job_application:
            raise ValidationError("Job application already exists for this job.")
        job_application = JobApplication.objects.create(
            **serializer.validated_data,
            job=job,
            applicant=master_profile,
            status=JobApplicationStatus.PENDING,
        )
        notify(
            verb="application_received",
            sender=job_application.applicant.user,
            recipient=job_application.job.employer.user,
            target=job_application.job,
            title=f"New Job Application for {job_application.job.title}",
            message=f"{job_application.applicant.user.get_full_name() or job_application.applicant.user.username} has applied to your job '{job_application.job.title}' with amount ${job_application.amount}.",
        )
        return Response(
            {
                "message": "Job application submitted successfully",
                "data": JobApplicationSerializer(job_application).data,
            },
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        description="Toggle bookmark status for a job",
        responses={
            200: CResponseSerializer,
        },
    )
    @action(detail=True, methods=["post"])
    def bookmark(self, request):
        job = self.get_object()
        bookmark, created = BookmarkJob.objects.get_or_create(
            user=request.user, job=job
        )
        if not created:
            bookmark.delete()
            return Response({
                'message': 'Job removed from bookmarks',
                "data": {
                    'is_bookmarked': False,
                }
            })
        return Response({
            'message': 'Job bookmarked successfully',
            "data": {
                'is_bookmarked': True,
            }
        })

    @extend_schema(
        description="Toggle favorite status for a job",
        responses={
            200: CResponseSerializer,
        },
    )
    @action(detail=True, methods=["post"])
    def favorite(self, request):
        job = self.get_object()
        favorite, created = FavoriteJob.objects.get_or_create(
            user=request.user, job=job
        )
        if not created:
            favorite.delete()
            return Response({
                'message': 'Job removed from favorites',
                "data": {
                    "is_favorited": False,
                },
            })
        return Response({
            'message': 'Job added to favorites',
            "data": {
                "is_favorited": True,
            },
        })


class _JobApplicationApiActionSerializer(CResponseSerializer):
    class _JobApplicationApiActionDataSerializer(serializers.Serializer):
        application = JobApplicationSerializer(read_only=True)

    data = _JobApplicationApiActionDataSerializer(read_only=True)


class JobApplicationAPIViewSet(ModelViewSet):
    """ViewSet for managing job applications."""

    permission_classes = [IsAuthenticated]
    serializer_class = JobApplicationSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = JobApplicationFilter
    search_fields = ["job__title", "job__description", "comment"]
    ordering_fields = ["created_at", "applied_at", "accepted_at", "withdrawn_at", "amount"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = JobApplication.objects.select_related("job", "applicant")
        user = self.request.user
        if hasattr(user, "employer_profile"):
            qs = qs.filter(job__employer=user.employer_profile)
        elif hasattr(user, "master_profile"):
            qs = qs.filter(applicant=user.master_profile)
        else:
            qs = JobApplication.objects.none()
        return qs

    @extend_schema(
        description="Accept a job application",
        responses={
            200: _JobApplicationApiActionSerializer,
        },
    )
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[
            IsAuthenticated,
            HasEmployerProfile,
            HasSpecificPermission(["jobs.change_jobapplication"]),
        ],
    )
    def accept(self, request, pk=None):
        try:
            application = JobApplication.objects.get(
                pk=pk,
                job__employer=request.user.employer_profile,
            )
        except JobApplication.DoesNotExist:
            raise NotFound("Job application not found")
        if application.status != JobApplicationStatus.PENDING:
            raise ValidationError("Only pending applications can be accepted.")

        with transaction.atomic():
            # Accept application
            application.status = JobApplicationStatus.ACCEPTED
            application.accepted_at = timezone.now()
            application.save()

            # Update job status
            job = application.job
            job.status = JobStatus.ASSIGNED
            job.assigned_at = timezone.now()
            job.save()

            # Create assignment
            assignment = JobAssignment.objects.create(
                job=job, master=application.applicant, accepted_application=application
            )

            # Reject other applications
            JobApplication.objects.filter(
                job=job, status=JobApplicationStatus.PENDING
            ).exclude(pk=pk).update(
                status=JobApplicationStatus.REJECTED, rejected_at=timezone.now()
            )
        try:
            chat_room = ChatRoom.objects.get(job=job)
            ChatParticipant.objects.get_or_create(
                chat_room=chat_room,
                user=request.user,
                defaults={"role": ChatRole.MEMBER, },
            )
        except ChatRoom.DoesNotExist:
            raise
        notify(
            verb="application_accepted",
            sender=application.job.employer.user,
            recipient=application.applicant.user,
            target=application.job,
            title=f"Your Application for {application.job.title} has been Accepted",
            message=f"Congratulations! Your application for the job '{application.job.title}' has been accepted by {application.job.employer.user.get_full_name() or application.job.employer.user.username}.",
        )

        return Response(
            {
                "message": "Job application accepted successfully",
                "data": {
                    "application": application,
                    "assignment": assignment,
                },
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        description="Reject a job application",
        responses={
            200: _JobApplicationApiActionSerializer,
        },
    )
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[
            IsAuthenticated,
            HasEmployerProfile,
            HasSpecificPermission(["jobs.change_jobapplication"]),
        ],
    )
    def reject(self, request, pk=None):
        try:
            application = JobApplication.objects.get(
                pk=pk,
                job__employer=request.user.employer_profile,
            )
        except JobApplication.DoesNotExist:
            raise NotFound("Job application not found")
        if application.status != JobApplicationStatus.PENDING:
            raise ValidationError("Only pending applications can be rejected.")
        application.status = JobApplicationStatus.REJECTED
        application.rejected_at = timezone.now()
        application.save()

        notify(
            verb="application_rejected",
            sender=application.job.employer.user,
            recipient=application.applicant.user,
            target=application.job,
            title=f"Your Application for {application.job.title} has been Rejected",
            message=f"We regret to inform you that your application for the job '{application.job.title}' has been rejected by {application.job.employer.user.get_full_name() or application.job.employer.user.username}.",
        )

        return Response(
            {
                "message": "Application rejected successfully",
                "data": {
                    "application": JobApplicationSerializer(application).data,
                },
            }
        )

    @extend_schema(
        description="Withdraw a job by master",
        responses={200: _JobApplicationApiActionSerializer},
    )
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated, HasMasterProfile],
    )
    def withdraw(self, request, pk=None):
        try:
            application = JobApplication.objects.get(
                pk=pk, applicant=request.user.master_profile
            )
        except JobApplication.DoesNotExist:
            raise NotFound("Job application not found")
        if application.status != JobApplicationStatus.PENDING:
            raise ValidationError("Only pending applications can be withdrawn.")
        application.status = JobApplicationStatus.WITHDRAWN
        application.withdrawn_at = timezone.now()
        application.save()
        return Response(
            {
                "message": "Application withdrawn successfully",
                "data": {
                    "application": JobApplicationSerializer(application).data,
                },
            }
        )


class _JobAssignmentApiActionSerializer(CResponseSerializer):
    class WrapperSerializer(serializers.Serializer):
        assignment = JobAssignmentSerializer(read_only=True)

    data = WrapperSerializer(read_only=True)


class JobAssignmentViewSet(ModelViewSet):
    queryset = JobAssignment.objects.select_related(
        "job", "master", "accepted_application"
    )
    serializer_class = JobAssignmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = JobAssignment.objects.all()
        user = self.request.user
        # if hasattr(user, "employer_profile"):
        #     qs = qs.filter(
        #
        #     )

    @extend_schema(
        description="Start an assignment",
        responses={
            200: _JobAssignmentApiActionSerializer,
        },
    )
    @action(detail=True, methods=["post"])
    def start(self, request):
        assignment = self.get_object()
        if assignment.status != JobAssignmentStatus.ASSIGNED:
            raise ValidationError("Assignment must be in ASSIGNED state to start.")
        assignment.status = JobAssignmentStatus.IN_PROGRESS
        assignment.started_at = timezone.now()
        assignment.save()

        assignment.job.status = JobStatus.IN_PROGRESS
        assignment.job.started_at = timezone.now()
        assignment.job.save()

        return Response(
            {
                "message": "Assignment started",
                "data": {
                    "assignment": JobAssignmentSerializer(assignment).data,
                },
            }
        )

    @extend_schema(
        description="Complete an assignment",
        responses={
            200: _JobAssignmentApiActionSerializer,
        },
    )
    @action(detail=True, methods=["post"])
    def complete(self, request):
        assignment = self.get_object()
        if assignment.status != JobAssignmentStatus.IN_PROGRESS:
            raise ValidationError("Assignment must be in progress to complete.")
        assignment.status = JobAssignmentStatus.COMPLETED
        assignment.completed_at = timezone.now()
        assignment.save()

        assignment.job.status = JobStatus.COMPLETED
        assignment.job.completed_at = timezone.now()
        assignment.job.save()

        return Response({
            "message": "Assignment completed",
            "data": {
                "assignment": JobAssignmentSerializer(assignment).data,
            },
        })

    @extend_schema(
        description="Update progress notes for an assignment",
        request=ProgressUpdateSerializer,
        responses={
            200: _JobAssignmentApiActionSerializer,
        },
    )
    @action(detail=True, methods=["patch"], permission_classes=[IsAuthenticated, HasMasterProfile])
    def update_progress(self, request):
        assignment = self.get_object()
        serializer = ProgressUpdateSerializer(assignment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "message": "Progress updated successfully",
            "data": {
                "assignment": JobAssignmentSerializer(assignment).data,
            },
        })

    @extend_schema(
        description="Rate a completed job assignment",
        request=RatingSerializer,
        responses={
            200: CResponseSerializer,
        },
    )
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def rate(self, request):
        assignment = self.get_object()
        if assignment.status != JobAssignmentStatus.COMPLETED:
            return Response({'error': 'Assignment must be completed to rate'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = RatingSerializer(assignment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Rating submitted successfully'})

#
# class UploadOrderAttachmentsAPIView(APIView):
#     """Upload attachments to order (before photos)."""
#     permission_classes = [IsAuthenticated]
#     parser_classes = [MultiPartParser, FormParser]
#
#     def post(self, request, pk):
#         """Upload attachments to order."""
#         try:
#             order = get_object_or_404(Order, pk=pk)
#
#             # Check permissions (client or assigned provider)
#             can_upload = (
#                     order.client.user_profile.user == request.user or
#                     OrderAssignment.objects.filter(
#                         order=order,
#                         provider__user_profile__user=request.user
#                     ).exists()
#             )
#
#             if not can_upload:
#                 return Response(
#                     {'error': 'Permission denied'},
#                     status=status.HTTP_403_FORBIDDEN
#                 )
#
#             # Handle file uploads
#             attachments = request.FILES.getlist('attachments')
#             uploaded_files = []
#
#             for attachment in attachments:
#                 order_attachment = OrderAttachment.objects.create(
#                     file_name=attachment.name,
#                     file_type=attachment.content_type.split('/')[0],
#                     file_size=attachment.size,
#                     file_url=attachment.url if hasattr(attachment, 'url') else '',
#                     mime_type=attachment.content_type,
#                     description=request.data.get('description', ''),
#                     uploaded_by=request.user
#                 )
#
#                 # Add to order
#                 order.attachments.add(order_attachment)
#                 uploaded_files.append({
#                     'id': order_attachment.id,
#                     'file_name': order_attachment.file_name,
#                     'file_type': order_attachment.file_type,
#                     'file_size': order_attachment.file_size
#                 })
#
#             return Response({
#                 'message': f'Uploaded {len(uploaded_files)} attachments',
#                 'attachments': uploaded_files
#             }, status=status.HTTP_201_CREATED)
#
#         except Exception as e:
#             return Response(
#                 {'error': f'Failed to upload attachments: {str(e)}'},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
#

#
# class RateClientAPIView(APIView):
#     """Rate client after job completion."""
#     permission_classes = [IsAuthenticated, HasServiceProviderProfile]
#
#     def post(self, request, pk):
#         """Rate client."""
#         try:
#             order = get_object_or_404(Order, pk=pk)
#
#             # Check if user is assigned to this order
#             assignment = get_object_or_404(
#                 OrderAssignment,
#                 order=order,
#                 provider__user_profile__user=request.user
#             )
#
#             if order.status != 'completed':
#                 return Response(
#                     {'error': 'Order must be completed to rate client'},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#
#             rating = request.data.get('rating')
#             review = request.data.get('review', '')
#
#             if not rating or not (1 <= int(rating) <= 5):
#                 return Response(
#                     {'error': 'Rating must be between 1 and 5'},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#
#             assignment.client_rating = int(rating)
#             assignment.client_review = review
#             assignment.save()
#
#             return Response({
#                 'message': 'Client rated successfully',
#                 'rating': assignment.client_rating,
#                 'review': assignment.client_review
#             }, status=status.HTTP_200_OK)
#
#         except Exception as e:
#             return Response(
#                 {'error': f'Failed to rate client: {str(e)}'},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
#

#

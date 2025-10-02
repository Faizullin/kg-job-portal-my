from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, parsers, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from job_portal.apps.attachments.models import create_attachments
from job_portal.apps.chats.models import ChatParticipant, ChatRole, ChatRoom
from job_portal.apps.notifications.models import notify
from job_portal.apps.users.api.permissions import HasEmployerProfile, HasMasterProfile
from utils.permissions import (
    HasSpecificPermission,
)
from utils.views import BaseAction, BaseActionAPIViewMixin
from .filters import JobApplicationFilter, JobFilter
from .permissions import JobAccessPermission
from .serializers import (
    CResponseSerializer,
    JobApplicationSerializer,
    JobApplySerializer,
    JobAssignmentAttachmentUploadSerializer,
    JobAssignmentCompletionSerializer,
    JobAssignmentSerializer,
    JobAttachmentUploadSerializer,
    JobSerializer,
    ProgressUpdateSerializer,
    RatingSerializer,
)
from ..models import (
    BookmarkJob,
    FavoriteJob,
    Job,
    JobApplication,
    JobApplicationStatus,
    JobAssignment,
    JobAssignmentStatus,
    JobStatus,
)
from ...attachments.api.permissions import IsAttachmentOwner
from ...attachments.serializers import AttachmentSerializer


class _JobApiActionSerializer(CResponseSerializer):
    data = JobSerializer(read_only=True)


class JobAPIViewSet(viewsets.ModelViewSet):
    """ViewSet for managing jobs."""

    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = JobSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = JobFilter
    filterset_fields = ["status", "service_subcategory", "urgency"]
    search_fields = ["title", "description", "special_requirements"]
    ordering_fields = [
        "created_at",
        "budget_min",
        "budget_max",
    ]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = Job.objects.all().select_related(
            "employer__user", "service_subcategory", "city"
        )
        user = self.request.user

        # Employer filtering
        if hasattr(user, "employer_profile"):
            qs = qs.filter(employer=user.employer_profile)
        # Master filtering - allow access to assigned jobs
        elif hasattr(user, "master_profile"):
            qs = qs.filter(
                Q(status=JobStatus.PUBLISHED)  # Published jobs
                | Q(assignment__master=user.master_profile)  # Assigned jobs
                | Q(applications__applicant=user.master_profile)  # Applied jobs
            ).distinct()
        else:
            qs = qs.filter(status=JobStatus.PUBLISHED)
        return qs

    def get_permissions(self):
        perms = super().get_permissions()
        if self.action == "list":
            pass
        elif self.action == "retrieve":
            perms += [JobAccessPermission()]
        elif self.action in [
            "update",
            "partial_update",
            "destroy",
            "publish",
            "cancel",
        ]:
            perms += [
                HasSpecificPermission(["jobs.change_job"])(),
                JobAccessPermission(),
            ]
        elif self.action == "create":
            perms += [HasSpecificPermission(["jobs.add_job"])()]
        elif self.action == "apply":
            perms += [
                IsAuthenticated(),
                HasMasterProfile(),
                HasSpecificPermission(["jobs.add_jobapplication"])(),
            ]
        return perms

    def perform_create(self, serializer):
        serializer.save(employer=self.request.user.employer_profile)

    @extend_schema(
        description="Publish a draft job. Only allowed if job is in DRAFT state.",
        responses={
            200: _JobApiActionSerializer,
        },
        operation_id="v1_jobs_publish",
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
        operation_id="v1_jobs_cancel",
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
        operation_id="v1_jobs_apply",
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
        operation_id="v1_jobs_bookmark",
    )
    @action(detail=True, methods=["post"])
    def bookmark(self, request):
        job = self.get_object()
        bookmark, created = BookmarkJob.objects.get_or_create(
            user=request.user, job=job
        )
        if not created:
            bookmark.delete()
            return Response(
                {
                    "message": "Job removed from bookmarks",
                    "data": {
                        "is_bookmarked": False,
                    },
                }
            )
        return Response(
            {
                "message": "Job bookmarked successfully",
                "data": {
                    "is_bookmarked": True,
                },
            }
        )

    @extend_schema(
        description="Toggle favorite status for a job",
        responses={
            200: CResponseSerializer,
        },
        operation_id="v1_jobs_favorite",
    )
    @action(detail=True, methods=["post"])
    def favorite(self, request):
        job = self.get_object()
        favorite, created = FavoriteJob.objects.get_or_create(
            user=request.user, job=job
        )
        if not created:
            favorite.delete()
            return Response(
                {
                    "message": "Job removed from favorites",
                    "data": {
                        "is_favorited": False,
                    },
                }
            )
        return Response(
            {
                "message": "Job added to favorites",
                "data": {
                    "is_favorited": True,
                },
            }
        )

    # Master Dashboard Actions
    @extend_schema(
        description="Get jobs currently in progress for master",
        responses={200: JobSerializer(many=True)},
        operation_id="v1_jobs_master_in_progress",
    )
    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated, HasMasterProfile],
    )
    def master_in_progress(self, request):
        """Get jobs currently in progress for master."""
        qs = Job.objects.filter(
            assignment__master=request.user.master_profile,
            assignment__status__in=[
                JobAssignmentStatus.ASSIGNED,
                JobAssignmentStatus.IN_PROGRESS,
            ],
        ).select_related("employer__user", "service_subcategory", "city")
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @extend_schema(
        description="Get completed job history for master",
        responses={200: JobSerializer(many=True)},
        operation_id="v1_jobs_master_history",
    )
    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated, HasMasterProfile],
    )
    def master_history(self, request):
        """Get completed job history for master."""
        qs = (
            Job.objects.filter(
                assignment__master=request.user.master_profile,
                assignment__status=JobAssignmentStatus.COMPLETED,
            )
            .select_related("employer__user", "service_subcategory", "city")
            .order_by("-assignment__completed_at")
        )
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class _JobApplicationApiActionSerializer(CResponseSerializer):
    class _JobApplicationApiActionDataSerializer(serializers.Serializer):
        application = JobApplicationSerializer(read_only=True)

    data = _JobApplicationApiActionDataSerializer(read_only=True)


class JobApplicationAPIViewSet(viewsets.ModelViewSet):
    """ViewSet for managing job applications."""

    permission_classes = [IsAuthenticated]
    serializer_class = JobApplicationSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = JobApplicationFilter
    search_fields = ["job__title", "job__description", "comment"]
    ordering_fields = [
        "created_at",
        "applied_at",
        "accepted_at",
        "withdrawn_at",
        "amount",
    ]
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
        operation_id="v1_applications_accept"
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
                defaults={
                    "role": ChatRole.MEMBER,
                },
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
        operation_id="v1_applications_accept_reject"
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
        operation_id="v1_applications_withdraw"
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


class JobAssignmentViewSet(BaseActionAPIViewMixin, viewsets.ModelViewSet):
    serializer_class = JobAssignmentSerializer
    permission_classes = [IsAuthenticated, HasMasterProfile]

    def get_queryset(self):
        qs = JobAssignment.objects.select_related(
            "job", "master", "accepted_application"
        ).filter(master=self.request.user.master_profile)
        return qs

    @extend_schema(
        description="Start an assignment",
        responses={
            200: _JobAssignmentApiActionSerializer,
        },
        operation_id="v1_job_assignments_start",
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
        description="Complete an assignment with optional rating and review",
        request=JobAssignmentCompletionSerializer,
        responses={
            200: _JobAssignmentApiActionSerializer,
        },
        operation_id="v1_job_assignments_complete",
    )
    @action(detail=True, methods=["post"])
    def complete(self, request):
        assignment = self.get_object()
        if assignment.status != JobAssignmentStatus.IN_PROGRESS:
            raise ValidationError("Assignment must be in progress to complete.")

        # Validate request data
        serializer = JobAssignmentCompletionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Extract validated data
        completion_notes = serializer.validated_data.get("completion_notes", "")
        client_rating = serializer.validated_data.get("client_rating")
        client_review = serializer.validated_data.get("client_review", "")

        # Update assignment
        assignment.status = JobAssignmentStatus.COMPLETED
        assignment.completed_at = timezone.now()
        assignment.completion_notes = completion_notes

        # Add rating and review if provided
        if client_rating is not None:
            assignment.client_rating = client_rating
        if client_review:
            assignment.client_review = client_review

        assignment.save()

        # Update job status
        assignment.job.status = JobStatus.COMPLETED
        assignment.job.completed_at = timezone.now()
        assignment.job.save()

        return Response(
            {
                "message": "Assignment completed successfully",
                "data": {
                    "assignment": JobAssignmentSerializer(assignment).data,
                },
            }
        )

    @extend_schema(
        description="Update progress notes for an assignment",
        request=ProgressUpdateSerializer,
        responses={
            200: _JobAssignmentApiActionSerializer,
        },
    )
    @action(
        detail=True,
        methods=["patch"],
        permission_classes=[IsAuthenticated, HasMasterProfile],
    )
    def update_progress(self, request):
        assignment = self.get_object()
        serializer = ProgressUpdateSerializer(
            assignment, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "message": "Progress updated successfully",
                "data": {
                    "assignment": JobAssignmentSerializer(assignment).data,
                },
            }
        )

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
            return Response(
                {"error": "Assignment must be completed to rate"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = RatingSerializer(assignment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Rating submitted successfully"})

    class TmpAction(BaseAction):
        pass

    available_actions = [
        TmpAction(),
    ]


class JobAttachmentAPIViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = [IsAuthenticated, IsAttachmentOwner, HasEmployerProfile]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def _get_job_obj(self) -> Job:
        if hasattr(self.request, "_job_obj"):
            return self.request._job_obj
        parent_lookup_field = "job_id"
        job_id = self.kwargs.get(parent_lookup_field)
        job = get_object_or_404(Job, id=job_id)
        if job.employer != self.request.user.employer_profile:
            raise PermissionDenied("You are not the owner of this job")
        self.request._job_obj = job
        return self.request._job_obj

    def get_queryset(self):
        job = self._get_job_obj()
        return job.attachments.all()

    def get_serializer_class(self):
        if self.action == "create":
            return JobAttachmentUploadSerializer
        return AttachmentSerializer

    def perform_create(self, serializer):
        job = self._get_job_obj()
        files = serializer.validated_data["files"]
        print("files", files)
        if not files:
            raise ValidationError("No files provided")
        attachments = create_attachments(files, self.request.user, job)
        for a in attachments:
            job.attachments.add(a)
        return attachments


class AssignmentAttachmentAPIViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = [IsAuthenticated, IsAttachmentOwner, HasMasterProfile]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def _get_job_assignment_obj(self) -> JobAssignment:
        if hasattr(self.request, "_job_assignment_obj"):
            return self.request._job_assignment_obj
        parent_lookup_field = "job_assignment_id"
        assignment_id = self.kwargs.get(parent_lookup_field)
        job_assignment = get_object_or_404(JobAssignment, id=assignment_id)
        if job_assignment.master != self.request.user.master_profile:
            raise PermissionDenied("You are not the owner of this job assignment")
        self.request._job_assignment_obj = job_assignment
        return self.request._job_assignment_obj

    def get_queryset(self):
        assignment = self._get_job_assignment_obj()
        return assignment.attachments.all()

    def get_serializer_class(self):
        if self.action == "create":
            return JobAssignmentAttachmentUploadSerializer
        return AttachmentSerializer

    def perform_create(self, serializer):
        assignment = self._get_job_assignment_obj()
        files = serializer.validated_data["files"]
        if not files:
            raise ValidationError("No files provided")
        attachments = create_attachments(files, self.request.user, assignment)
        for a in attachments:
            assignment.attachments.add(a)
        return attachments

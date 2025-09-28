from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .serializers import MasterResumeSerializer
from ..models import MasterResume, ResumeStatus
from ...users.api.permissions import HasMasterProfile


class MasterResumeAPIViewSet(ModelViewSet):
    """CRUD for Master resumes. Masters manage their own resumes, public sees published."""

    serializer_class = MasterResumeSerializer
    permission_classes = [IsAuthenticated, HasMasterProfile]


    def get_queryset(self):
        qs = MasterResume.objects.select_related("master__user")

        if hasattr(self.request.user, "master_profile"):
            return qs.filter(master=self.request.user.master_profile)

        return qs.filter(status=ResumeStatus.PUBLISHED)

    def perform_create(self, serializer):
        if not hasattr(self.request.user, "master_profile"):
            raise ValidationError("Only Masters can create resumes.")
        serializer.save(master=self.request.user.master_profile)

    @extend_schema(
        description="Publish a draft resume. Only allowed if in DRAFT state.",
        responses={
            200: OpenApiResponse(description="Resume published"),
        },
    )
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        resume = self.get_object()
        if resume.status != ResumeStatus.DRAFT:
            raise ValidationError("Resume cannot be published in its current state.")
        resume.status = ResumeStatus.PUBLISHED
        resume.save()
        return Response({"message": "Resume published successfully"})

    @extend_schema(
        description="Archive a published resume.",
        responses={
            200: OpenApiResponse(
                description="Resume archived",
            )
        }
    )
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        resume = self.get_object()
        if resume.status != ResumeStatus.PUBLISHED:
            raise ValidationError("Only published resumes can be archived.")
        resume.status = ResumeStatus.ARCHIVED
        resume.save()
        return Response({"message": "Resume archived successfully"})

from django.core.validators import FileExtensionValidator, get_available_image_extensions
from rest_framework import serializers

from job_portal.apps.attachments.serializers import AttachmentSerializer
from job_portal.apps.jobs.models import Job, JobApplication, JobAssignment, JobStatus
from job_portal.apps.users.api.serializers import UserDetailChildSerializer
from job_portal.apps.users.models import Employer, Master
from utils.serializers import AbstractTimestampedModelSerializer


class EmployerBasicSerializer(serializers.ModelSerializer):
    """Basic employer information for job serialization."""

    user = UserDetailChildSerializer(read_only=True)

    class Meta:
        model = Employer
        fields = ["id", "user", "total_orders", "completed_orders", "cancelled_orders"]


class JobSerializer(AbstractTimestampedModelSerializer):
    attachments = AttachmentSerializer(many=True, read_only=True)
    employer = EmployerBasicSerializer(read_only=True)

    class Meta:
        model = Job
        fields = [
            "id",
            "employer",
            "service_subcategory",
            "title",
            "description",
            "status",
            "location",
            "city",
            "service_date",
            "service_time",
            "urgency",
            "budget_min",
            "budget_max",
            "final_price",
            "special_requirements",
            "attachments",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "employer", "created_at", "updated_at"]


class JobApplicationSerializer(AbstractTimestampedModelSerializer):
    job = JobSerializer(read_only=True)

    class Meta:
        model = JobApplication
        fields = [
            "id",
            "job",
            "applicant",
            "status",
            "applied_at",
            "accepted_at",
            "rejected_at",
            "withdrawn_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "applied_at",
            "accepted_at",
            "rejected_at",
            "withdrawn_at",
            "created_at",
            "updated_at",
        ]


class JobApplySerializer(AbstractTimestampedModelSerializer):
    job_id = serializers.PrimaryKeyRelatedField(
        queryset=Job.objects.filter(status=JobStatus.PUBLISHED),
        source="job",
        write_only=True,
        help_text="ID of the job to apply for",
    )

    class Meta:
        model = JobApplication
        fields = [
            "id",
            "job_id",
            "amount",
            "comment",
            "estimated_duration",
            "resume",
            "status",
            "applied_at",
            "accepted_at",
            "rejected_at",
            "withdrawn_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "applied_at",
            "accepted_at",
            "rejected_at",
            "withdrawn_at",
            "created_at",
            "updated_at",
        ]


class AssignmentMasterSerializer(AbstractTimestampedModelSerializer):
    user = UserDetailChildSerializer(read_only=True)

    class Meta:
        model = Master
        fields = [
            "id",
            "user",
        ]
        read_only_fields = ["id"]


class JobAssignmentSerializer(AbstractTimestampedModelSerializer):
    job = JobSerializer(read_only=True)
    master = AssignmentMasterSerializer(read_only=True)
    accepted_application = JobApplicationSerializer(read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = JobAssignment
        fields = [
            "id",
            "status",
            "assigned_at",
            "started_at",
            "completed_at",
            "progress_notes",
            "completion_notes",
            "client_rating",
            "client_review",
            "job",
            "master",
            "accepted_application",
            "attachments",
        ]
        read_only_fields = ["id", "assigned_at"]


class CResponseSerializer(serializers.Serializer):
    message = serializers.CharField(
        help_text="A message describing the result of the operation."
    )
    data = serializers.JSONField()


class ProgressUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobAssignment
        fields = ["id", "progress_notes"]
        read_only_fields = [
            "id",
        ]


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobAssignment
        fields = ["id", "client_rating", "client_review"]
        read_only_fields = [
            "id",
        ]


class JobAssignmentCompletionSerializer(serializers.ModelSerializer):
    """Serializer for completing job assignments with rating and review."""

    completion_notes = serializers.CharField(
        required=False, allow_blank=True, help_text="Notes about the completion"
    )
    attachments = AttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = JobAssignment
        fields = [
            "id",
            "completion_notes",
            "attachments",
        ]
        read_only_fields = ["id"]


def validate_file_size(file_obj):
    max_size = 1024 * 1024  # 1MB
    if file_obj.size > max_size:
        raise serializers.ValidationError(f"File is larger than {max_size=}")


def validate_total_size(file_list):
    total_size = sum(f.size for f in file_list)
    max_mb_size = 10
    max_size = 1024 * 1024 * max_mb_size
    if total_size > max_size:
        current_mb = total_size / (1024 * 1024)
        raise serializers.ValidationError(
            f"The total size of all attachments ({current_mb:.2f} MB) "
            f"exceeds the maximum allowed total size of {max_mb_size:.0f} MB."
        )


class JobAttachmentUploadSerializer(serializers.Serializer):
    """Serializer for job assignment attachments."""

    files = serializers.ListField(
        child=serializers.FileField(
            validators=[
                FileExtensionValidator(allowed_extensions=get_available_image_extensions()),
                validate_file_size,
            ],
        ),
        allow_empty=False,
        write_only=True,
        validators=[validate_total_size]
    )


class JobAssignmentAttachmentUploadSerializer(serializers.Serializer):
    """Serializer for creating job assignment attachments."""

    files = serializers.ListField(
        child=serializers.FileField(
            validators=[
                FileExtensionValidator(allowed_extensions=get_available_image_extensions()),
                validate_file_size,
            ],
        ),
        allow_empty=False,
        write_only=True,
        validators=[validate_total_size]
    )

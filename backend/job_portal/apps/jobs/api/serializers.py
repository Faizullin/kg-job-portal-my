from rest_framework import serializers

from job_portal.apps.jobs.models import Job, JobApplication, JobStatus, JobAssignment
from job_portal.apps.users.api.serializers import UserDetailChildSerializer
from job_portal.apps.users.models import Master
from utils.serializers import (
    AbstractTimestampedModelSerializer
)


class JobSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = Job
        fields = [
            'id', 'employer', 'service_subcategory', 'title', 'description', 'status',
            'location', 'city', 'service_date', 'service_time',
            'urgency', 'budget_min', 'budget_max', 'final_price',
            'special_requirements', 'created_at', 'updated_at'
        ]


class JobApplicationSerializer(AbstractTimestampedModelSerializer):
    job = JobSerializer(read_only=True)

    class Meta:
        model = JobApplication
        fields = [
            'id', 'job', 'applicant', 'status', 'applied_at', 'accepted_at', 'rejected_at', 'withdrawn_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'applied_at', 'accepted_at', 'rejected_at', 'withdrawn_at', 'created_at',
                            'updated_at']


class JobApplySerializer(AbstractTimestampedModelSerializer):
    job_id = serializers.PrimaryKeyRelatedField(
        queryset=Job.objects.filter(status=JobStatus.PUBLISHED),
        source='job',
        write_only=True,
        help_text="ID of the job to apply for"
    )

    class Meta:
        model = JobApplication
        fields = ['id', 'job_id', 'amount', 'comment', 'estimated_duration', 'resume', 'status', 'applied_at',
                  'accepted_at', 'rejected_at', 'withdrawn_at',
                  'created_at', 'updated_at'
                  ]
        read_only_fields = ['id', 'status', 'applied_at', 'accepted_at', 'rejected_at', 'withdrawn_at', 'created_at',
                            'updated_at']


class AssignmentMasterSerializer(AbstractTimestampedModelSerializer):
    user = UserDetailChildSerializer(read_only=True)

    class Meta:
        model = Master
        fields = ["id", "user", ]
        read_only_fields = ["id"]


class JobAssignmentSerializer(AbstractTimestampedModelSerializer):
    job = JobSerializer(read_only=True)
    master = AssignmentMasterSerializer(read_only=True)
    accepted_application = JobApplicationSerializer(read_only=True)

    class Meta:
        model = JobAssignment
        fields = [
            'id', 'status', 'assigned_at', 'started_at', 'completed_at', 'progress_notes',
            'completion_notes', 'client_rating', 'client_review',
            'job', 'master', 'accepted_application'
        ]
        read_only_fields = ['id', 'assigned_at']


class CResponseSerializer(serializers.Serializer):
    message = serializers.CharField(
        help_text="A message describing the result of the operation."
    )
    data = serializers.JSONField()


class ProgressUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobAssignment
        fields = ['id', 'progress_notes']
        read_only_fields = ["id", ]


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobAssignment
        fields = ['id', 'client_rating', 'client_review']
        read_only_fields = ["id", ]

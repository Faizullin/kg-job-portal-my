from rest_framework import serializers
from utils.serializers import AbstractTimestampedModelSerializer
from job_portal.apps.users.api.serializers import UserDetailChildSerializer
from job_portal.apps.jobs.api.serializers import JobSerializer
from job_portal.apps.users.models import Master
from ..models import Review, AppFeedback


class MasterBasicSerializer(serializers.ModelSerializer):
    """Basic master serializer for review data."""
    user = UserDetailChildSerializer(read_only=True)
    
    class Meta:
        model = Master
        fields = ['id', 'user']


class ReviewSerializer(AbstractTimestampedModelSerializer):
    """Serializer for reading review data with nested serializers."""

    reviewer = UserDetailChildSerializer(read_only=True)
    master = MasterBasicSerializer(read_only=True)
    job = JobSerializer(read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "job",
            "reviewer",
            "master",
            "rating",
            "title",
            "comment",
            "is_verified",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "is_verified", "created_at", "updated_at"]


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new reviews with OpenAPI documentation."""

    class Meta:
        model = Review
        fields = ["job", "master", "rating", "title", "comment"]
        extra_kwargs = {
            "rating": {
                "help_text": "Rating from 1 to 5 stars",
                "min_value": 1,
                "max_value": 5,
            },
            "title": {"help_text": "Brief title for the review", "max_length": 200},
            "comment": {"help_text": "Detailed review comment", "max_length": 1000},
        }

    def validate_rating(self, value):
        """Validate rating is between 1 and 5."""
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def validate(self, attrs):
        """Validate that the job belongs to the master and user can review it."""
        job = attrs.get("job")
        master = attrs.get("master")

        if job and master:
            # Check if the job is completed
            if job.status != "completed":
                raise serializers.ValidationError(
                    "You can only review completed jobs."
                )

            # Check if review already exists for this job
            if Review.objects.filter(
                job=job, reviewer=self.context["request"].user
            ).exists():
                raise serializers.ValidationError(
                    "You have already reviewed this job."
                )

        return attrs


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating existing reviews."""

    class Meta:
        model = Review
        fields = ["rating", "title", "comment"]

    def validate_rating(self, value):
        """Validate rating is between 1 and 5."""
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


class ReviewAnalyticsSerializer(serializers.Serializer):
    """Serializer for review analytics data with OpenAPI support."""

    total_reviews = serializers.IntegerField(help_text="Total number of reviews")
    average_rating = serializers.DecimalField(
        max_digits=3, decimal_places=2, help_text="Average rating across all reviews"
    )
    rating_distribution = serializers.ListField(
        child=serializers.DictField(), help_text="Distribution of ratings (1-5 stars)"
    )


class ClientRatingSerializer(serializers.Serializer):
    """Serializer for client rating from OrderAssignment model."""

    rating = serializers.IntegerField(
        min_value=1, max_value=5, help_text="Client rating from 1 to 5 stars"
    )
    review = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        help_text="Optional review text about the client",
    )

    def validate_rating(self, value):
        """Validate rating is between 1 and 5."""
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


class JobAssignmentReviewSerializer(serializers.Serializer):
    """Serializer for job assignment with review data."""

    job_id = serializers.IntegerField(help_text="Job ID")
    job_title = serializers.CharField(help_text="Job title")
    master_name = serializers.CharField(help_text="Master name")
    client_name = serializers.CharField(help_text="Client name")
    client_rating = serializers.IntegerField(
        allow_null=True, help_text="Client rating (1-5 stars)"
    )
    client_review = serializers.CharField(
        allow_null=True, allow_blank=True, help_text="Client review text"
    )
    master_rating = serializers.IntegerField(
        allow_null=True, help_text="Master rating (1-5 stars)"
    )
    master_review = serializers.CharField(
        allow_null=True, allow_blank=True, help_text="Master review text"
    )
    completed_at = serializers.DateTimeField(help_text="Job completion date")


class AppFeedbackSerializer(AbstractTimestampedModelSerializer):
    """Serializer for app feedback and rating system."""

    user = UserDetailChildSerializer(read_only=True)

    class Meta:
        model = AppFeedback
        fields = (
            "id",
            "user",
            "general_opinion",
            "detailed_feedback",
            "overall_rating",
            "design_feedback",
            "usability_feedback",
            "bug_report",
            "missing_features",
            "everything_satisfies",
            "app_version",
            "device_info",
            "platform",
            "is_reviewed",
            "admin_notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "user",
            "is_reviewed",
            "admin_notes",
            "created_at",
            "updated_at",
        )

    def validate_overall_rating(self, value):
        """Validate overall rating is between 1 and 5."""
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Overall rating must be between 1 and 5.")
        return value


class AppFeedbackCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating app feedback."""

    class Meta:
        model = AppFeedback
        fields = (
            "general_opinion",
            "detailed_feedback",
            "overall_rating",
            "design_feedback",
            "usability_feedback",
            "bug_report",
            "missing_features",
            "everything_satisfies",
            "app_version",
            "device_info",
            "platform",
        )

    def validate_overall_rating(self, value):
        """Validate overall rating is between 1 and 5."""
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Overall rating must be between 1 and 5.")
        return value

from rest_framework import serializers

from lms.apps.posts.models import Post
from lms.apps.resources.api.serializers import PostAuthorSerializer


class RecordPostSerializer(serializers.ModelSerializer):
    author = PostAuthorSerializer()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "author",
            "category",
            "created_at",
            "updated_at",
            "publication_status",
            "meta_title",
            "content_type",
            "object_id",
            "content",
        ]


class LogReportSerializer(serializers.ModelSerializer):
    author = PostAuthorSerializer()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "author",
            "category",
            "created_at",
            "updated_at",
            "publication_status",
            "meta_title",
            "content_type",
            "object_id",
            "content",
        ]
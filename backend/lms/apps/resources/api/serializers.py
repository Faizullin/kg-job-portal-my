from django.contrib.auth import get_user_model
from rest_framework import serializers

from lms.apps.posts.models import Post, Category, Tag

User = get_user_model()


class PostAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
        ]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "title", "term", "description", "created_at", "updated_at"]


class PostSubmitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "category",
            "created_at",
            "updated_at",
            "publication_status",
            "meta_title",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.author:
            representation["author"] = PostAuthorSerializer(instance.author).data
        if instance.category:
            representation["category"] = CategorySerializer(instance.category).data
        return representation


class PostSerializer(serializers.ModelSerializer):
    author = PostAuthorSerializer()
    category = CategorySerializer()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "slug",
            "author",
            "category",
            "created_at",
            "updated_at",
            "publication_status",
            "meta_title",
            "content_type",
            "object_id",
            "post_type",
        ]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = [
            "id",
            "title",
        ]

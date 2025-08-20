from time import timezone
from rest_framework import serializers

from lms.apps.core.models import PublicationStatus
from lms.apps.posts.models import Post
from lms.apps.resources.api.serializers import CategorySerializer, PostAuthorSerializer
from lms.apps.resources.models import (
    TemplateComponent,
    VimeoUrlCacheModel,
    get_video_link_from_vimeo,
)
from django.utils import timezone


class BasePostEditSerializer(serializers.Serializer):
    post_id = serializers.IntegerField(required=True, write_only=True)


class PostSerializer(serializers.ModelSerializer):
    author = PostAuthorSerializer()
    category = CategorySerializer()

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
        ]


class SaveContentSerializer(BasePostEditSerializer):
    """
    Serializer for saving content.
    """

    content = serializers.CharField(required=True)


class PublishContentSerializer(BasePostEditSerializer):
    """
    Serializer for building and publishing content.
    """

    publication_status = serializers.ChoiceField(
        choices=PublicationStatus.choices,
        required=True,
        help_text="Publication status of the post.",
    )


class TemplateComponentSerializer(serializers.ModelSerializer):
    """
    Serializer for TemplateComponent.
    """

    class Meta:
        model = TemplateComponent
        fields = [
            "id",
            "title",
            "content",
            "component_type",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class MediaLibAttachmentUploadSerializer(BasePostEditSerializer):
    """
    Serializer for uploading media library attachments.
    """

    file = serializers.FileField(required=True)


class VimeoUrlCacheSerializer(serializers.ModelSerializer):
    class Meta:
        model = VimeoUrlCacheModel
        fields = [
            "id",
            "vimeo_link",
            "playable_video_link",
            "expire_time",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "playable_video_link",
            "expire_time",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        vimeo_link = validated_data["vimeo_link"]
        new_data = get_video_link_from_vimeo(vimeo_link)
        new_obj = VimeoUrlCacheModel.objects.create(
            vimeo_link=vimeo_link,
            playable_video_link=new_data["link"],
            expire_time=new_data["expire_time"],
        )
        return new_obj
    
    def update(self, instance, validated_data):
        vimeo_link = validated_data.get("vimeo_link", instance.vimeo_link)
        new_data = get_video_link_from_vimeo(vimeo_link)
        instance.vimeo_link = vimeo_link
        instance.playable_video_link = new_data["link"]
        instance.expire_time = new_data["expire_time"]
        instance.save()
        return instance
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        now = timezone.now() - timezone.timedelta(seconds=20)
        # check if expired
        if instance.expire_time and instance.expire_time < now:
            new_data = get_video_link_from_vimeo(instance.vimeo_link)
            instance.playable_video_link = new_data["link"]
            instance.expire_time = new_data["expire_time"]
            instance.save()
        representation["playable_video_link"] = instance.playable_video_link
        representation["expire_time"] = instance.expire_time.isoformat()
        representation["vimeo_link"] = instance.vimeo_link
        representation["updated_at"] = instance.updated_at.isoformat()
        return representation

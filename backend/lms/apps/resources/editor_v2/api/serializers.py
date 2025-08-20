from django.db import transaction
from rest_framework import serializers

from api_lessons.models import LessonPage, LessonPageElement
from api_lessons.models.lesson_components import (
    # media & simple
    AudioComponent,
    ImageComponent,
    RecordAudioComponent,
    TextComponent,
    VideoComponent,
    # question
    QuestionComponent,
    QuestionAnswer,
    # fill-text
    FillTextComponent,
    FillTextLine,
    # put-in-order
    PutInOrderComponent,
    PutInOrderComponentElement,
)
from api_lessons.serializers.components_serializers import BlueCardComponentSerializer
from backend.global_function import ModelIntegerField
from lms.apps.posts.models import Post
from lms.apps.resources.api.serializers import CategorySerializer, PostAuthorSerializer
from lms.apps.resources.utils import get_video_link_from_vimeo


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


class BuildAndPublishContentSerializer(BasePostEditSerializer):
    """
    Serializer for building and publishing content.
    """

    content = serializers.CharField(required=True)


class LoadComponentObjDataItemSerializer(serializers.Serializer):
    component_type = serializers.CharField(required=True)
    object_id = serializers.IntegerField(required=True)


class LoadComponentObjDataSerializer(BasePostEditSerializer):
    items = LoadComponentObjDataItemSerializer(many=True, required=True)


# ───────────────────────────────────────────────────────────────
# utilities
# ───────────────────────────────────────────────────────────────
class _ItemIdMixin:
    """Adds write-only ``item_id`` for bulk update_or_create."""

    item_id = serializers.IntegerField(write_only=True, required=False)


class FileControlSerializer(BasePostEditSerializer):
    ACTION_CHOICES = (
        ("upload", "Upload"),
        ("remove", "Remove"),
    )

    file_action = serializers.ChoiceField(choices=ACTION_CHOICES)
    file = serializers.FileField(required=False, allow_null=True)
    component_name = serializers.CharField()
    file_field_name = serializers.CharField()
    object_id = serializers.IntegerField()

    def validate(self, data):
        file_action = data.get("file_action")
        file = data.get("file", None)

        if file_action == "upload":
            if file is None:
                raise serializers.ValidationError(
                    {"file": "File is required for upload."}
                )

            # Optional: Include format and size validation here
            self.validate_file_format(file)
            self.validate_file_size(file)

        elif file_action == "remove":
            if file:
                raise serializers.ValidationError(
                    {"file": "File should not be provided for remove."}
                )

        return data

    def validate_file_format(self, file):
        allowed_mime_types = ["image/jpeg", "image/png", "audio/mpeg"]
        if file.content_type not in allowed_mime_types:
            raise serializers.ValidationError({"file": "Unsupported file format."})

    def validate_file_size(self, file, file_size_limit_b=None):
        if file_size_limit_b is None:
            file_size_limit_b = 10 * 1024 * 1024  # Default to 10MB
        max_size_mb = int(file_size_limit_b / (1024 * 1024))  # Convert bytes to MB
        if file.size > file_size_limit_b:
            raise serializers.ValidationError(
                {"file": f"File size exceeds {max_size_mb}MB."}
            )


# ───────────────────────────────────────────────────────────────
# media components (audio / image)
# ───────────────────────────────────────────────────────────────
class AudioComponentSerializer(serializers.ModelSerializer):
    audio = serializers.SerializerMethodField()
    audio_file = serializers.FileField(write_only=True, required=False)

    class Meta:
        model = AudioComponent
        fields = ["id", "title", "audio", "audio_file"]

    # read
    def get_audio(self, obj):
        return None if not obj.audio else {"url": obj.audio.url}

    # write
    def create(self, validated):
        file_obj = validated.pop("audio_file", None)
        instance = AudioComponent.objects.create(**validated)
        if file_obj:
            instance.audio = file_obj
            instance.save()
        return instance

    def update(self, instance, validated):
        file_obj = validated.pop("audio_file", None)
        for k, v in validated.items():
            setattr(instance, k, v)
        if file_obj:
            if instance.audio:
                instance.audio.delete(save=False)
            instance.audio = file_obj
        instance.save()
        return instance


class ImageComponentSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    image_file = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = ImageComponent
        fields = ["id", "description", "image", "image_file"]

    def get_image(self, obj):
        return None if not obj.image else {"url": obj.image.url}

    def create(self, validated):
        file_obj = validated.pop("image_file", None)
        instance = ImageComponent.objects.create(**validated)
        if file_obj:
            instance.image = file_obj
            instance.save()
        return instance

    def update(self, instance, validated):
        file_obj = validated.pop("image_file", None)
        for k, v in validated.items():
            setattr(instance, k, v)
        if file_obj:
            if instance.image:
                instance.image.delete(save=False)
            instance.image = file_obj
        instance.save()
        return instance


# ───────────────────────────────────────────────────────────────
# simple flat components
# ───────────────────────────────────────────────────────────────
class TextProComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextComponent
        fields = ["id", "title", "text"]


class RecordingComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordAudioComponent
        fields = ["id", "title", "description"]


class VideoComponentSerializer(serializers.ModelSerializer):
    embedded_video_url = serializers.SerializerMethodField()

    class Meta:
        model = VideoComponent
        fields = ["id", "description", "video_url", "embedded_video_url"]

    def get_embedded_video_url(self, obj):
        return get_video_link_from_vimeo(obj.video_url)


# ───────────────────────────────────────────────────────────────
# QUESTION component  (answers nested)
# ───────────────────────────────────────────────────────────────
class QuestionAnswerSerializer(_ItemIdMixin, serializers.ModelSerializer):
    item_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = QuestionAnswer
        fields = ["id", "text", "is_correct", "item_id"]


class QuestionComponentSerializer(serializers.ModelSerializer):
    answers = QuestionAnswerSerializer(many=True)

    class Meta:
        model = QuestionComponent
        fields = ["id", "text", "answers"]

    # ───── write helpers ───── #
    @transaction.atomic
    def create(self, validated):
        answers_data = validated.pop("answers", [])
        q = QuestionComponent.objects.create(**validated)
        QuestionAnswer.objects.bulk_create(
            QuestionAnswer(component=q, text=a["text"], is_correct=a["is_correct"])
            for a in answers_data
        )
        return q

    @transaction.atomic
    def update(self, instance, validated):
        answers_data = validated.pop("answers", [])
        instance.text = validated.get("text", instance.text)
        instance.save()

        keep_ids = []
        for a in answers_data:
            obj, _ = QuestionAnswer.objects.update_or_create(
                id=a.get("item_id"),
                defaults={
                    "component": instance,
                    "text": a["text"],
                    "is_correct": a["is_correct"],
                },
            )
            keep_ids.append(obj.id)
        instance.answers.exclude(id__in=keep_ids).delete()
        return instance


# ───────────────────────────────────────────────────────────────
# FILL-TEXT component  (lines nested)
# ───────────────────────────────────────────────────────────────
class FillTextLineSerializer(_ItemIdMixin, serializers.ModelSerializer):
    class Meta:
        model = FillTextLine
        fields = ["id", "text_before", "answer", "text_after", "order", "item_id"]


class FillTextComponentSerializer(serializers.ModelSerializer):
    lines = FillTextLineSerializer(many=True)

    class Meta:
        model = FillTextComponent
        fields = ["id", "title", "put_words", "lines"]

    @transaction.atomic
    def create(self, validated):
        lines = validated.pop("lines", [])
        ft = FillTextComponent.objects.create(**validated)
        FillTextLine.objects.bulk_create(
            FillTextLine(
                component=ft,
                text_before=l["text_before"],
                answer=l["answer"],
                text_after=l["text_after"],
                order=l["order"],
            )
            for l in lines
        )
        return ft

    @transaction.atomic
    def update(self, instance, validated):
        lines = validated.pop("lines", [])
        for attr, val in validated.items():
            setattr(instance, attr, val)
        instance.save()

        keep_ids = []
        for l in lines:
            obj, _ = FillTextLine.objects.update_or_create(
                id=l.get("item_id"),
                defaults={
                    "component": instance,
                    "text_before": l["text_before"],
                    "answer": l["answer"],
                    "text_after": l["text_after"],
                    "order": l["order"],
                },
            )
            keep_ids.append(obj.id)
        instance.lines.exclude(id__in=keep_ids).delete()
        return instance


# ───────────────────────────────────────────────────────────────
# PUT-IN-ORDER component  (elements nested)
# ───────────────────────────────────────────────────────────────
class PutInOrderComponentElementSerializer(_ItemIdMixin, serializers.ModelSerializer):
    class Meta:
        model = PutInOrderComponentElement
        fields = ["id", "text", "order", "item_id"]


class OrderComponentElementSerializer(serializers.ModelSerializer):
    elements = PutInOrderComponentElementSerializer(many=True)

    class Meta:
        model = PutInOrderComponent
        fields = ["id", "title", "elements"]

    @transaction.atomic
    def create(self, validated):
        elements = validated.pop("elements", [])
        comp = PutInOrderComponent.objects.create(**validated)
        PutInOrderComponentElement.objects.bulk_create(
            PutInOrderComponentElement(
                component=comp,
                text=e["text"],
                order=e["order"],
            )
            for e in elements
        )
        return comp

    @transaction.atomic
    def update(self, instance, validated):
        elements = validated.pop("elements", [])
        instance.title = validated.get("title", instance.title)
        instance.save()

        keep_ids = []
        for e in elements:
            obj, _ = PutInOrderComponentElement.objects.update_or_create(
                id=e.get("item_id"),
                defaults={
                    "component": instance,
                    "text": e["text"],
                    "order": e["order"],
                },
            )
            keep_ids.append(obj.id)
        instance.elements.exclude(id__in=keep_ids).delete()
        return instance


class LessonPageElementSerializer(serializers.ModelSerializer):
    blue_card_component = BlueCardComponentSerializer(
        many=False, allow_null=True, required=False
    )
    audio_component = AudioComponentSerializer(
        many=False, allow_null=True, required=False
    )
    # matching_component = MatchingComponentSerializer(many=False, allow_null=True, required=False)
    record_audio_component = RecordingComponentSerializer(
        many=False, allow_null=True, required=False
    )
    video_component = VideoComponentSerializer(
        many=False, allow_null=True, required=False
    )
    put_in_order_component = OrderComponentElementSerializer(
        many=False, allow_null=True, required=False
    )
    text_component = TextProComponentSerializer(
        many=False, allow_null=True, required=False
    )
    fill_text_component = FillTextComponentSerializer(
        many=False, allow_null=True, required=False
    )
    question_component = QuestionComponentSerializer(
        many=False, allow_null=True, required=False
    )
    image_component = ImageComponentSerializer(
        many=False, allow_null=True, required=False
    )

    page = ModelIntegerField(source="page.id", model=LessonPage)

    class Meta:
        model = LessonPageElement
        fields = "__all__"

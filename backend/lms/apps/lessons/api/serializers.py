from django.contrib.auth import get_user_model
from rest_framework import serializers

from api_lessons.models import Lesson, LessonBatch, LessonPage

User = get_user_model()


class LessonBatchSerializer(serializers.ModelSerializer):
    lesson_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = LessonBatch
        fields = (
            "id",
            "title",
            "lesson_count",
        )


class LessonSubmitSerializer(serializers.ModelSerializer):
    order = serializers.IntegerField(required=False)

    class Meta:
        model = Lesson
        fields = [
            "id",
            "is_available_on_free",
            "lesson_batch",
            "title",
            "description",
            "order",
        ]


class LessonBatchConnectedSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonBatch
        fields = (
            "id",
            "title",
        )


class LessonSerializer(serializers.ModelSerializer):
    lesson_batch = LessonBatchConnectedSerializer()

    class Meta:
        model = Lesson
        fields = [
            "id",
            "is_available_on_free",
            "lesson_batch",
            "title",
            "description",
            "order",
        ]


class LessonPageSerializer(serializers.ModelSerializer):
    order = serializers.IntegerField(required=False)

    class Meta:
        model = LessonPage
        fields = [
            "id",
            "lesson",
            "order",
            "title",
        ]


class LessonPageReorderSubmitSerializer(serializers.Serializer):
    lesson_id = serializers.PrimaryKeyRelatedField(queryset=Lesson.objects.all())
    ordered_ids = serializers.ListField(child=serializers.IntegerField())

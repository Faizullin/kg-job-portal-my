from django.contrib.auth import get_user_model
from rest_framework import serializers

from lms.apps.questions.models import (
    Question,
    MultipleChoiceOption,
    OrderingItem,
    FillGapBlank,
    MatchingElement,
    MatchingPair,
    RecordAudioSettings,
    QuestionTypes,
)

User = get_user_model()


class QuestionEditBaseSerializer(serializers.Serializer):
    """Base serializer for question editing"""

    id = serializers.IntegerField(required=False, help_text="Question ID")
    text = serializers.CharField(required=True, help_text="The text of the question")
    question_type = serializers.ChoiceField(
        choices=QuestionTypes.choices, help_text="Type of the question"
    )


class MultipleChoiceOptionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = MultipleChoiceOption
        fields = ["id", "text", "is_correct", "order"]


class MultipleChoiceOptionSubmitSerializer(QuestionEditBaseSerializer):
    """Serializer for submitting multiple choice answers"""

    answers = MultipleChoiceOptionSerializer(
        many=True,
        required=True,
    )


class AnswerToMultipleChoiceQuestionSerializer(serializers.Serializer):
    answers = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        help_text="List of IDs of selected answers",
    )



class OrderingItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = OrderingItem
        fields = ["id", "text", "correct_order"]


class OrderingItemSubmitSerializer(QuestionEditBaseSerializer):
    """Serializer for submitting ordering answers"""

    items = OrderingItemSerializer(
        many=True,
        required=True,
    )

class AnswerToOrderingQuestionSerializer(serializers.Serializer):
    """Serializer for submitting answers to ordering questions"""

    items = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField(),
            required=True,
            help_text="List of dictionaries with item ID and its order"
        ),
        required=True,
        help_text="List of answers for each ordering item"
    )

class FillGapBlankSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    correct_answers = serializers.ListField(
        child=serializers.CharField(), required=False, allow_empty=True
    )

    class Meta:
        model = FillGapBlank
        fields = [
            "id",
            "index",
            "correct_answers",
            "question_id",
        ]


class QuestionFillGapBlankSubmitSerializer(QuestionEditBaseSerializer):
    """Serializer for submitting fill gap blank answers"""

    blanks = FillGapBlankSerializer(
        many=True,
        required=True,
    )
    

class AnswerToFillGapBlankQuestionSerializer(serializers.Serializer):
    """Serializer for submitting answers to fill gap blank questions"""

    blanks = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField(),
            required=True,
            help_text="List of dictionaries with index and answer text"
        ),
        required=True,
        help_text="List of answers for each fill gap blank"
    )


class MatchingElementSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    image = serializers.SerializerMethodField(
        read_only=True, help_text="Image URL for the matching element"
    )

    class Meta:
        model = MatchingElement
        fields = ["id", "text", "image"]

    def get_image(self, obj: MatchingElement):
        if obj.image:
            return {
                "id": obj.image.id,
                "url": obj.image.url,
                "name": obj.image.name,
            }
        return None


class MatchingPairSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    left_element_id = serializers.IntegerField(
        required=True, help_text="ID of the left matching element"
    )
    right_element_id = serializers.IntegerField(
        required=True, help_text="ID of the right matching element"
    )
    
    class Meta:
        model = MatchingPair
        fields = [
            "id",
            "left_element_id",
            "right_element_id",
        ]


class MatchingQuestionSaveAllSubmitSerializer(QuestionEditBaseSerializer):
    """Serializer for submitting matching question with all components"""

    pairs = MatchingPairSerializer(
        many=True,
        required=True,
        help_text="List of matching pairs with left and right elements",
    )


class MatchingElementSubmitSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    image_file = serializers.FileField(
        write_only=True, required=False, help_text="Image file for the matching element"
    )
    image = serializers.SerializerMethodField(
        read_only=True, help_text="Image URL for the matching element"
    )

    class Meta:
        model = MatchingElement
        fields = ["id", "text", "image", "image_file"]

    def get_image(self, obj):
        if obj.image:
            return {
                "id": obj.image.id,
                "url": obj.image.file.url if obj.image.file else None,
                "name": obj.image.file.name if obj.image.file else None,
            }
        return None


class AnswerToMatchingQuestionSerializer(serializers.Serializer):
    """Serializer for submitting answers to matching questions"""

    pairs = MatchingPairSerializer(
        many=True,
        required=True,
        help_text="List of matching pairs with left and right elements",
    )


class RecordAudioSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordAudioSettings
        fields = ["id", "title", "instructions"]


class RecordAudioQuestionSubmitSerializer(QuestionEditBaseSerializer):
    """Serializer for submitting record audio questions"""

    record_audio_settings = RecordAudioSettingsSerializer(required=True)

class AnswerToRecordAudioQuestionSerializer(serializers.Serializer):
    """Serializer for submitting answers to record audio questions"""

    file = serializers.FileField(
        required=True, help_text="Audio file submitted by the user"
    )

class QuestionCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating basic questions"""

    class Meta:
        model = Question
        fields = ["id", "text", "question_type"]

    def create(self, validated_data):
        # Create basic question without any nested components
        return Question.objects.create(**validated_data)


class QuestionListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""

    class Meta:
        model = Question
        fields = ["id", "text", "question_type", "created_at", "updated_at"]


class QuestionSerializer(serializers.ModelSerializer):
    """Basic question serializer - only handles Question model fields"""

    class Meta:
        model = Question
        fields = [
            "id",
            "text",
            "question_type",
            "created_at",
            "updated_at",
        ]

    def update(self, instance, validated_data):
        # Only update basic Question fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class QuestionComponentsSubmitSerializer(serializers.Serializer):
    """Serializer for submitting question components"""

    action = serializers.CharField(required=True, help_text="Action to perform")
    # any data field thet laso can contain innner file: Example: {"data": {"text": "Example text", "image_file": <file>}}
    data = serializers.DictField(
        required=True,
        help_text="Data for the action, can include nested fields like text, image_file, etc.",
    )


class QuestionComponentsUplaodSubmitSerializer(serializers.Serializer):
    """Serializer for submitting question components"""

    action = serializers.CharField(required=True, help_text="Action to perform")


class QuestionPublicUserCheckSubmitSerializer(serializers.Serializer):
    """Serializer for submitting user answers to questions"""

    question_id = serializers.IntegerField(required=True, help_text="ID of the question")
    answer_data = serializers.DictField(
        required=True,
        help_text="Data containing user's answer, can vary based on question type",
    )
    form_data_type = serializers.ChoiceField(
        choices=["upload", "json"],
        required=True,
        help_text="Type of the answer, either 'upload' for file upload or 'json' for JSON data",
    )
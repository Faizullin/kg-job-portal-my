from abc import ABC, abstractmethod
import json
from lms.apps.attachments.models import Attachment
from rest_framework import serializers
from django.db import transaction
from django.contrib.contenttypes.models import ContentType

from lms.apps.questions.models import (
    Question,
    MultipleChoiceOption,
    OrderingItem,
    FillGapBlank,
    MatchingElement,
    MatchingPair,
    RecordAudioSettings,
    QuestionTypes,
    UserAnswer,
)
from .serializers import (
    AnswerToFillGapBlankQuestionSerializer,
    AnswerToMatchingQuestionSerializer,
    AnswerToMultipleChoiceQuestionSerializer,
    AnswerToRecordAudioQuestionSerializer,
    MatchingElementSubmitSerializer,
    MatchingQuestionSaveAllSubmitSerializer,
    MultipleChoiceOptionSerializer,
    MultipleChoiceOptionSubmitSerializer,
    OrderingItemSerializer,
    FillGapBlankSerializer,
    MatchingElementSerializer,
    MatchingPairSerializer,
    OrderingItemSubmitSerializer,
    QuestionFillGapBlankSubmitSerializer,
    RecordAudioQuestionSubmitSerializer,
    RecordAudioSettingsSerializer,
)


class BaseQuestionComponentRepository(ABC):
    """Abstract base class for question component providers"""

    def __init__(self, question: Question):
        self.question = question

    @abstractmethod
    def handle(self, action_name, data=None):
        raise NotImplementedError("handle method must be implemented in the subclass")
    
    @abstractmethod
    def submit_user_answer(self, data):
        """Method to submit user answer for the question component."""
        raise NotImplementedError("submit_user_answer method must be implemented in the subclass")


class MultipleChoiceRepository(BaseQuestionComponentRepository):
    """Repository for multiple choice questions"""

    def get_answers_qs(self):
        """Get queryset of multiple choice options for the question."""
        return self.question.mc_options.all()

    def get_answer_object(self, data):
        component_id = data.get("id")
        if not component_id:
            raise serializers.ValidationError("Component ID is required")
        try:
            return self.get_answers_qs().get(id=component_id)
        except MultipleChoiceOption.DoesNotExist:
            raise serializers.ValidationError("Component not found")

    def load_all(self):
        components = self.get_answers_qs().order_by("order")
        return {
            "id": self.question.id,
            "text": self.question.text,
            "answers": MultipleChoiceOptionSerializer(components, many=True).data,
        }

    def save_all(self, data):
        serializer = MultipleChoiceOptionSubmitSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        answers_data = serializer.validated_data.get("answers", [])
        with transaction.atomic():
            delete_exclude_ids = []
            for item in answers_data:
                if item.get("id"):
                    # Update existing component
                    component = self.get_answer_object({"id": item.get("id")})
                    i_serializer = MultipleChoiceOptionSerializer(
                        component, data=item, partial=True
                    )
                else:
                    # Create new component
                    i_serializer = MultipleChoiceOptionSerializer(data=item)

                i_serializer.is_valid(raise_exception=True)
                item = i_serializer.save(question=self.question)
                delete_exclude_ids.append(item.id)
            self.question.text = serializer.validated_data.get(
                "text", self.question.text
            )
            self.question.save()
            self.get_answers_qs().exclude(id__in=delete_exclude_ids).delete()
        return self.load_all()
    
    def submit_user_answer(self, data, request):
        """Submit user answer for multiple choice question."""
        serializer = AnswerToMultipleChoiceQuestionSerializer(data=data["answer_data"])
        serializer.is_valid(raise_exception=True)
        user = request.user
        initial_answer, created = UserAnswer.objects.get_or_create(
            user=user,
            question=self.question,
            defaults={},
        )
        json_answer_response_data = {}
        with transaction.atomic():
            for answer_id in serializer.validated_data.get("answers", []):
                try:
                    answer = self.get_answer_object({"id": answer_id})
                except serializers.ValidationError as e:
                    raise serializers.ValidationError(f"Invalid answer ID: {answer_id}. {str(e)}")
            
            json_answer_response_data = {
                "answers": serializer.validated_data.get("answers", []),
                "answers_data": {
                    "question_id": self.question.id,
                    "question_type": self.question.question_type,
                    "question_text": self.question.text,
                }
            }
            initial_answer.data = json.dumps(json_answer_response_data)
            initial_answer.save()
    
        return {
            "id": initial_answer.id,
            "question_id": self.question.id,
            "status": "success",
            "answer": {
                "status": ("updated" if not created else "created") if json_answer_response_data is not None else "error",
                "data": json_answer_response_data,
            }
        }

    def handle(self, action_name, data=None, request=None):
        if action_name == "load-all":
            return self.load_all()
        elif action_name == "save-all":
            return self.save_all(data)
        elif action_name == "submit_user_answer":
            return self.submit_user_answer(data, request)
        else:
            raise serializers.ValidationError(
                f"Invalid action: {action_name}. Supported actions: load-all, save-all"
            )


class OrderingRepository(BaseQuestionComponentRepository):
    """Repository for ordering questions"""

    def get_items_qs(self):
        """Get queryset of ordering items for the question."""
        return self.question.ordering_items.all()

    def get_item_object(self, data):
        component_id = data.get("id")
        if not component_id:
            raise serializers.ValidationError("Component ID is required")
        try:
            return self.get_items_qs().get(id=component_id)
        except OrderingItem.DoesNotExist:
            raise serializers.ValidationError("Component not found")

    def load_all(self):
        components = self.get_items_qs().order_by("correct_order")
        return {
            "id": self.question.id,
            "text": self.question.text,
            "items": OrderingItemSerializer(components, many=True).data,
        }

    def save_all(self, data):
        serializer = OrderingItemSubmitSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        items_data = serializer.validated_data.get("items", [])
        with transaction.atomic():
            delete_exclude_ids = []
            for item in items_data:
                if item.get("id"):
                    # Update existing component
                    component = self.get_item_object({"id": item.get("id")})
                    i_serializer = OrderingItemSerializer(
                        component, data=item, partial=True
                    )
                else:
                    # Create new component
                    i_serializer = OrderingItemSerializer(data=item)

                i_serializer.is_valid(raise_exception=True)
                item = i_serializer.save(question=self.question)
                delete_exclude_ids.append(item.id)

            self.question.text = serializer.validated_data.get(
                "text", self.question.text
            )
            self.question.save()
            self.get_items_qs().exclude(id__in=delete_exclude_ids).delete()
        return self.load_all()
    
    def submit_user_answer(self, data, request):
        serializer = OrderingItemSubmitSerializer(data=data["answer_data"])
        serializer.is_valid(raise_exception=True)
        user = request.user
        initial_answer, created = UserAnswer.objects.get_or_create(
            user=user,
            question=self.question,
            defaults={},
        )
        json_answer_response_data = {}
        with transaction.atomic():
            items_data = serializer.validated_data.get("items", [])
            if not items_data:
                raise serializers.ValidationError("Items data is required")

            json_answer_response_data = {
                "answers": items_data,
                "question_id": self.question.id,
                "question_type": self.question.question_type,
                "question_text": self.question.text,
            }
            initial_answer.data = json.dumps(json_answer_response_data)
            initial_answer.save()
        return {
            "id": initial_answer.id,
            "question_id": self.question.id,
            "status": "success",
            "answer": {
                "status": ("updated" if not created else "created") if json_answer_response_data is not None else "error",
                "data": json_answer_response_data,
            }
        }

    def handle(self, action_name, data=None, request=None):
        if action_name == "load-all":
            return self.load_all()

        elif action_name == "save-all":
            return self.save_all(data)

        elif action_name == "submit_user_answer":
            return self.submit_user_answer(data, request)

        raise serializers.ValidationError(
            f"Invalid action: {action_name}. Supported actions: load-all, save-all"
        )


class FillGapBlankRepository(BaseQuestionComponentRepository):
    """Repository for fill in the blank questions"""

    def get_blanks_qs(self):
        """Get queryset of fill in the blank lines for the question."""
        return self.question.fill_gap_blanks.all()

    def get_blank_object(self, data):
        component_id = data.get("id")
        if not component_id:
            raise serializers.ValidationError("Component ID is required")
        try:
            return self.get_blanks_qs().get(id=component_id)
        except FillGapBlank.DoesNotExist:
            raise serializers.ValidationError("Component not found")

    def load_all(self):
        """Get components with question text together."""
        components = self.get_blanks_qs().order_by("index")
        return {
            "id": self.question.id,
            "text": self.question.text,
            "blanks": FillGapBlankSerializer(components, many=True).data,
        }

    def save_all(self, data):
        """Save all fill in the blank lines and question text in a single transaction.
        Deletes blanks that are not present in the submitted data (by exclusion).
        First creates/updates, then deletes unused ones.
        """

        serializer = QuestionFillGapBlankSubmitSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        blanks_data = serializer.validated_data.get("blanks", [])
        with transaction.atomic():
            delete_exclude_ids = []

            # Create or update blanks
            for item in blanks_data:
                if item.get("id"):
                    # Update existing component
                    component = self.get_blank_object({"id": item.get("id")})
                    i_serializer = FillGapBlankSerializer(
                        component, data=item, partial=True
                    )
                else:
                    # Create new component
                    i_serializer = FillGapBlankSerializer(data=item)

                i_serializer.is_valid(raise_exception=True)
                item = i_serializer.save(question=self.question)
                delete_exclude_ids.append(item.id)

            self.question.text = serializer.validated_data.get(
                "text", self.question.text
            )
            self.question.save()
            self.get_blanks_qs().exclude(id__in=delete_exclude_ids).delete()

        return self.load_all()
    
    def submit_user_answer(self, data, request):
        """Submit user answer for fill in the blank question."""
        serializer = AnswerToFillGapBlankQuestionSerializer(data=data["answer_data"])
        serializer.is_valid(raise_exception=True)
        user = request.user
        initial_answer, created = UserAnswer.objects.get_or_create(
            user=user,
            question=self.question,
            defaults={},
        )
        json_answer_response_data = {}
        with transaction.atomic():
            blanks_data = serializer.validated_data.get("blanks", [])
            if not blanks_data:
                raise serializers.ValidationError("Blanks data is required")

            json_answer_response_data = {
                "answers": blanks_data,
                "question_id": self.question.id,
                "question_type": self.question.question_type,
                "question_text": self.question.text,
            }
            initial_answer.data = json.dumps(json_answer_response_data)
            initial_answer.save()

        return {
            "id": initial_answer.id,
            "question_id": self.question.id,
            "status": "success",
            "answer": {
                "status": ("updated" if not created else "created") if json_answer_response_data is not None else "error",
                "data": json_answer_response_data,
            }
        }

    def handle(self, action_name, data=None, request=None):
        if action_name == "load-all":
            return self.load_all()
        elif action_name == "save-all":
            return self.save_all(data)
        elif action_name == "submit_user_answer":
            return self.submit_user_answer(data, request)
        raise serializers.ValidationError(
            f"Invalid action: {action_name}. Supported actions: load-all, save-all"
        )


class MatchingProvider(BaseQuestionComponentRepository):
    """Provider for matching questions"""

    def load_all(self):
        elements = self.question.matching_elements.all()
        pairs = self.question.matching_pairs.all()
        return {
            "id": self.question.id,
            "text": self.question.text,
            "elements": MatchingElementSerializer(elements, many=True).data,
            "pairs": MatchingPairSerializer(pairs, many=True).data,
        }

    def get_elements_qs(self):
        """Get queryset of matching elements for the question."""
        return self.question.matching_elements.all()

    def get_element_object(self, data) -> MatchingElement:
        component_id = data.get("id")
        if not component_id:
            raise serializers.ValidationError("Component ID is required")
        try:
            return self.get_elements_qs().get(id=component_id)
        except MatchingElement.DoesNotExist:
            raise serializers.ValidationError("Component not found")

    def save_element(self, request_data, request):
        element_obj = None
        element_id = request_data.get("id", None)
        if element_id is not None:
            element_obj = MatchingElement.objects.get(id=element_id)
        serializer_kwargs = {
            "data": request_data,
        }
        if element_obj is not None:
            serializer_kwargs["instance"] = element_obj
        serializer = MatchingElementSubmitSerializer(**serializer_kwargs)
        serializer.is_valid(raise_exception=True)
        image_file = serializer.validated_data.pop("image_file", None)
        item = serializer.save(question=self.question)
        if image_file is not None:
            new_attachment_obj = Attachment.objects.create(
                file=image_file,
                attachment_type="file",
                file_type="image",
                content_type=ContentType.objects.get_for_model(MatchingElement),
                object_id=item.id,
            )
            new_file_url = request.build_absolute_uri(new_attachment_obj.file.url)
            new_attachment_obj.url = new_file_url
            new_attachment_obj.save()
            item.image = new_attachment_obj
            item.save()
        return MatchingElementSerializer(item).data

    def check_pair_elements_existence(self, left_element_id, right_element_id):
        """Check if both elements in a pair exist."""
        elements_qs = self.get_elements_qs()
        if not elements_qs.filter(id=left_element_id).exists():
            raise serializers.ValidationError(
                f"Left element {left_element_id} does not exist"
            )
        if not elements_qs.filter(id=right_element_id).exists():
            raise serializers.ValidationError(
                f"Right element {right_element_id} does not exist"
            )
            
    def check_pair_uniqueness(self, left_id, right_id, exclude_id=None):
        """Check if the pair of elements is unique, excluding a specific pair ID."""
        pairs_qs = self.question.matching_pairs.all()
        if exclude_id:
            pairs_qs = pairs_qs.exclude(id=exclude_id)
        if pairs_qs.filter(left_element_id=left_id, right_element_id=right_id).exists():
            raise serializers.ValidationError(
                f"Pair ({left_id}, {right_id}) already exists"
            )

    def save_all(self, data):
        """Save all matching question components in a single transaction."""
        serializer = MatchingQuestionSaveAllSubmitSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            delete_exclude_pairs_ids = []
            
            pairs_data = serializer.validated_data.get("pairs", [])
            for item in pairs_data:
                left_id = item.get("left_element_id")
                right_id = item.get("right_element_id")
                self.check_pair_elements_existence(left_id, right_id)
                # check uniqiness except for the current pair
                if item.get("id"):
                    self.check_pair_uniqueness(left_id, right_id, exclude_id=item.get("id"))

            pairs_save_data: list[MatchingPair] = []
            for item in pairs_data:
                if item.get("id"):
                    # Update existing pair
                    pair = self.question.matching_pairs.get(id=item.get("id"))
                    i_serializer = MatchingPairSerializer(pair, data=item, partial=True)
                else:
                    # Create new pair
                    i_serializer = MatchingPairSerializer(data=item)

                i_serializer.is_valid(raise_exception=True)
                save_el = MatchingPair(**i_serializer.validated_data, question=self.question)
                # item = i_serializer.save(question=self.question)
                pairs_save_data.append(save_el)
                
                if save_el.id:
                    delete_exclude_pairs_ids.append(save_el.id)

            # Delete pairs that are not present in the submitted data
            self.question.matching_pairs.exclude(id__in=delete_exclude_pairs_ids).delete()
        
            if pairs_save_data:
                create_data = [
                    pair for pair in pairs_save_data if pair.id is None
                ]
                update_data = [
                    pair for pair in pairs_save_data if pair.id is not None
                ]
                if create_data:
                    MatchingPair.objects.bulk_create(create_data)
                if update_data:
                    MatchingPair.objects.bulk_update(
                        update_data, ["left_element", "right_element"]
                    )
                    
            self.question.text = data.get("text", self.question.text)
            self.question.save()
            

        return self.load_all()

    def delete_element(self, data):
        """Delete a matching element by its ID."""
        component = self.get_element_object(data)
        if component.image:
            component.image.delete()  # Delete associated image if exists
        component.delete()
        return True

    def submit_user_answer(self, data, request):
        """Submit user answer for matching question."""
        serializer = AnswerToMatchingQuestionSerializer(data=data["answer_data"])
        serializer.is_valid(raise_exception=True)
        user = request.user
        initial_answer, created = UserAnswer.objects.get_or_create(
            user=user,
            question=self.question,
            defaults={},
        )
        json_answer_response_data = {}
        with transaction.atomic():
            pairs_data = serializer.validated_data.get("pairs", [])
            if not pairs_data:
                raise serializers.ValidationError("Pairs data is required")

            json_answer_response_data = {
                "answers": pairs_data,
                "question_id": self.question.id,
                "question_type": self.question.question_type,
                "question_text": self.question.text,
            }
            initial_answer.data = json.dumps(json_answer_response_data)
            initial_answer.save()

        return {
            "id": initial_answer.id,
            "question_id": self.question.id,
            "status": "success",
            "answer": {
                "status": ("updated" if not created else "created") if json_answer_response_data is not None else "error",
                "data": json_answer_response_data,
            }
        }

    def handle(self, action_name, data=None, request=None):
        if action_name == "load-all":
            return self.load_all()
        elif action_name == "save-element":
            return self.save_element(data, request)
        elif action_name == "save-all":
            return self.save_all(data)
        elif action_name == "delete-element":
            return self.delete_element(data)
        elif action_name == "submit_user_answer":
            return self.submit_user_answer(data, request)
        raise serializers.ValidationError(
            f"Invalid action: {action_name}. Supported actions: load-all, save-element, save-all, delete-element"
        )


class RecordAudioProvider(BaseQuestionComponentRepository):
    """Provider for record audio questions"""

    def load_all(self, question):
        component, _ = RecordAudioSettings.objects.get_or_create(
            question=question, defaults={"title": question.text, "instructions": ""}
        )
        return {
            "id": question.id,
            "text": question.text,
            "record_audio_settings": RecordAudioSettingsSerializer(component).data,
        }

    def save_all(self, data):
        serializer = RecordAudioQuestionSubmitSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            # Update or create record audio settings
            record_audio_settings, created = (
                RecordAudioSettings.objects.update_or_create(
                    question=self.question,
                    defaults=serializer.validated_data.get("record_audio_settings"),
                )
            )

            self.question.text = serializer.validated_data.get(
                "title", self.question.text
            )
            self.question.save()

        return self.load_all(self.question)
    
    def submit_user_answer(self, data, request):
        serializer = AnswerToRecordAudioQuestionSerializer(data=data["answer_data"])
        serializer.is_valid(raise_exception=True)
        user_answer, created = UserAnswer.objects.get_or_create(
            user=request.user,
            question=self.question,
            defaults={},
        )
        json_answer_response_data = {}
        with transaction.atomic():
            file = serializer.validated_data.get("file")
            if not file:
                raise serializers.ValidationError("Audio file is required")

            # Save the audio file as an attachment
            attachment = Attachment.objects.create(
                file=file,
                attachment_type="file",
                file_type="audio",
                content_type=ContentType.objects.get_for_model(UserAnswer),
                object_id=user_answer.id,
            )
            new_file_url = request.build_absolute_uri(attachment.file.url)
            attachment.url = new_file_url
            attachment.save()

            json_answer_response_data = {
                "answers": {
                    "id": attachment.id,
                    "url": new_file_url,
                    "name": attachment.file.name,
                },
                "question_id": self.question.id,
                "question_type": self.question.question_type,
                "question_text": self.question.text,
            }
            user_answer.data = json.dumps(json_answer_response_data)
            user_answer.save()
        return {
            "id": user_answer.id,
            "question_id": self.question.id,
            "status": "success",
            "answer": {
                "status": ("updated" if not created else "created") if json_answer_response_data is not None else "error",
                "data": json_answer_response_data,
            }
        }

    def handle(self, action_name, data=None, request=None):
        if action_name == "load-all":
            return self.load_all(self.question)
        elif action_name == "save-all":
            return self.save_all(data)
        elif action_name == "submit_user_answer":
            return self.submit_user_answer(data, request)
        raise serializers.ValidationError(
            f"Invalid action: {action_name}. Supported actions: load-all, save-all"
        )


class QuestionProviderFactory:
    """Factory to get the appropriate provider for a question type"""

    _repo_classes = {
        QuestionTypes.MULTIPLE_CHOICE: MultipleChoiceRepository,
        QuestionTypes.ORDERING: OrderingRepository,
        QuestionTypes.FILL_IN_THE_BLANKS: FillGapBlankRepository,
        QuestionTypes.MATCHING: MatchingProvider,
        QuestionTypes.RECORD_AUDIO: RecordAudioProvider,
    }

    @classmethod
    def get_provider(cls, question: Question):
        provider: BaseQuestionComponentRepository = cls._repo_classes.get(
            question.question_type
        )
        if not provider:
            raise ValueError(f"No provider found for question type: {question_type}")
        return provider(question)

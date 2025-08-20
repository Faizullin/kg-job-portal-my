from api_users.permissions import IsAuthenticatedWithBlocked
from django_filters import CharFilter, ChoiceFilter
from django_filters.rest_framework import FilterSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from lms.apps.core.utils.crud_base.views import BaseApiViewSet, BaseApiView
from lms.apps.questions.models import (
    Question,
    QuestionTypes,
)
from .serializers import (
    QuestionComponentsSubmitSerializer,
    QuestionComponentsUplaodSubmitSerializer,
    QuestionPublicUserCheckSubmitSerializer,
    QuestionSerializer,
    QuestionListSerializer,
    QuestionCreateSerializer,
)
from .components_repositories import QuestionProviderFactory


class QuestionViewSet(BaseApiViewSet):
    search_fields = ["text"]
    ordering_fields = ["id", "created_at", "updated_at"]

    class QuestionFilter(FilterSet):
        text = CharFilter(lookup_expr="icontains")
        question_type = ChoiceFilter(choices=QuestionTypes.choices)

        class Meta:
            model = Question
            fields = ["id", "text", "question_type"]

    filterset_class = QuestionFilter

    def get_queryset(self):
        return Question.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return QuestionCreateSerializer
        elif self.action == "list":
            return QuestionListSerializer
        return QuestionSerializer

    @action(detail=True, methods=["post"])
    def components(self, request, pk=None):
        """Get components for a question based on its type"""
        question = self.get_object()
        serializer = QuestionComponentsSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            provider = QuestionProviderFactory.get_provider(question)
            components = provider.handle(
                serializer.validated_data["action"], serializer.validated_data["data"]
            )
            return Response(components)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=True, methods=["post"])
    def components_attachments_upload(self, request, pk=None):
        """List all components for a question"""
        question = self.get_object()
        serializer = QuestionComponentsUplaodSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            provider = QuestionProviderFactory.get_provider(question)
            components = provider.handle(serializer.validated_data["action"], request.data, request)
            return Response(components)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class QuestionPublicUserSubmitApiView(BaseApiView):
    """
    API view for submitting a question by a user and grading it.
    """
    
    permission_classes = [IsAuthenticatedWithBlocked]

    def post(self, request, *args, **kwargs):
        serializer = QuestionPublicUserCheckSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            question = Question.objects.get(id=serializer.validated_data["question_id"])
        except Question.DoesNotExist:
            return Response({"error": "Question not found."}, status=status.HTTP_404_NOT_FOUND)
        try:
            provider = QuestionProviderFactory.get_provider(question)
            response_data = provider.handle(
                "submit_user_answer",
                serializer.validated_data,
                request,
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "message": "Question submitted successfully.",
            "data": response_data
            }, status=status.HTTP_201_CREATED)
    
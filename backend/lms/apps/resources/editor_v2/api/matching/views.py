from api_lessons.models.lesson_components.matching_component import (
    MatchingComponent,
)
from lms.apps.core.utils.crud_base.views import BaseApiViewSet
from .serializers import (
    MatchingComponentCreateUpdateSerializer,
    MatchingComponentDetailSerializer,
    MatchingComponentListSerializer,
)


class MatchingComponentViewSet(BaseApiViewSet):
    search_fields = [
        "title",
    ]

    def get_queryset(self):
        return MatchingComponent.objects.all().prefetch_related("element_couples")

    def get_serializer_class(self):
        if self.action == "list":
            return MatchingComponentListSerializer
        elif self.action == "retrieve":
            return MatchingComponentDetailSerializer
        return MatchingComponentCreateUpdateSerializer

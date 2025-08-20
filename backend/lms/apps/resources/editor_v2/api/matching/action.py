from lms.apps.core.utils.api_actions import (
    ActionRequestException,
    BaseAction,
    BaseActionException,
)
from lms.apps.resources.editor_v2.api.matching.utils import components_elements_qs
from .serializers import (
    MatchingComponentFileControlSerializer,
    MatchingComponentDetailSerializer,
)
from api_lessons.models.lesson_components.matching_component import (
    MatchingComponent,
    MatchingComponentElement,
)


class MatchingFileControlAction(BaseAction):
    name = "matching-file-control"

    def apply(self, request):
        serializer = MatchingComponentFileControlSerializer(data=request.data)
        if not serializer.is_valid():
            raise ActionRequestException(serializer.errors)
        file_action_name = serializer.validated_data["file_action"]
        try:
            component_obj = MatchingComponent.objects.get(
                pk=serializer.validated_data["object_id"]
            )
        except MatchingComponent.DoesNotExist:
            raise ActionRequestException("`object_id` is invalid")
        except Exception as e:
            raise BaseActionException(str(e))
        try:
            used_elements_ids = components_elements_qs(component_obj).values_list("id", flat=True)
            if serializer.validated_data["element_id"] not in used_elements_ids:
                raise ActionRequestException(
                    "The provided `element_id` is not used in any element couple of this matching component"
                )
            element_obj = MatchingComponentElement.objects.get(
                pk=serializer.validated_data["element_id"],
            )
        except MatchingComponentElement.DoesNotExist:
            raise ActionRequestException("`element_id` is invalid")
        except Exception as e:
            raise BaseActionException(str(e))
        if file_action_name == "upload":
            if element_obj.image:
                element_obj.image.delete(save=False)
            element_obj.image = serializer.validated_data["file"]
            element_obj.save()
            return {
                "success": 1,
                "data": {
                    "message": "File uploaded successfully",
                    "component_data": MatchingComponentDetailSerializer(
                        component_obj
                    ).data,
                },
            }
        elif file_action_name == "remove":
            if not element_obj.image:
                raise ActionRequestException(
                    f"No file found for matching component image file field"
                )
            element_obj.image.delete(save=False)
            element_obj.image = None
            element_obj.save()
            return {
                "success": 1,
                "data": {
                    "message": "File removed successfully",
                    "component_data": MatchingComponentDetailSerializer(
                        component_obj
                    ).data,
                },
            }

import json

from rest_framework import status
from rest_framework.response import Response

from api_lessons.models import (
    TextComponent,
    QuestionComponent,
    BlueCardComponent,
    AudioComponent,
    FillTextComponent,
    PutInOrderComponent,
    VideoComponent,
    ImageComponent,
    RecordAudioComponent,
)
from api_lessons.models.lesson_components.__component_base import LessonPage
from api_lessons.models.lesson_components.__page_element import LessonPageElement
from api_lessons.serializers.components_serializers import (
    BlueCardComponentSerializer,
    LessonPageSerializer,
)
from lms.apps.core.utils.api_actions import (
    BaseAction,
    BaseActionException,
    ActionRequestException,
)
from lms.apps.core.utils.crud_base.views import BaseApiViewSet, BaseApiView
from lms.apps.posts.models import Post
from lms.apps.resources.editor_v2.api.matching.action import (
    MatchingFileControlAction,
)
from lms.apps.resources.editor_v2.api.serializers import (
    AudioComponentSerializer,
    FillTextComponentSerializer,
    ImageComponentSerializer,
    OrderComponentElementSerializer,
    QuestionComponentSerializer,
    RecordingComponentSerializer,
    TextProComponentSerializer,
    VideoComponentSerializer,
    LessonPageElementSerializer,
)
from .components_utils import (
    COMPONENT_NAME_TO_COMPONENT_MODEL_CLASS_DICT,
    COMPONENT_NAME_TO_ELEMENT_FIELD_NAME_DICT,
)
from .matching.serializers import MatchingComponentCreateUpdateSerializer
from .matching.views import MatchingComponentViewSet
from .serializers import (
    BasePostEditSerializer,
    BuildAndPublishContentSerializer,
    FileControlSerializer,
    LoadComponentObjDataSerializer,
    PostSerializer,
    SaveContentSerializer,
)


class LoadContentAction(BaseAction):
    name = "load-content"

    def apply(self, request):
        serializer = BasePostEditSerializer(data=request.data)
        if not serializer.is_valid():
            raise ActionRequestException(serializer.errors)
        try:
            post_obj = Post.objects.get(pk=serializer.validated_data["post_id"])
        except Post.DoesNotExist:
            raise BaseActionException("`post_id` is invalid")
        except Exception as e:
            raise BaseActionException(str(e))
        LessonPageModel = post_obj.content_type.model_class()
        try:
            page_obj = LessonPageModel.objects.get(pk=post_obj.object_id)
        except LessonPageModel.DoesNotExist:
            raise BaseActionException("`object_id` is invalid")
        except Exception as e:
            raise BaseActionException(str(e))
        json_instance_data = PostSerializer(post_obj).data
        json_instance_data["content_type"] = page_obj._meta.model_name
        json_instance_data["object_id"] = post_obj.object_id
        return {
            "success": 1,
            "data": {
                "content": post_obj.content,
                "instance": json_instance_data,
                # "elements": [
                #     {
                #         "id": el.id,
                #         "component_type": el.component_type,
                #         "component_id": el.id,
                #         "order": el.order,
                #     } for el in page_obj.elements.all()
                # ]
            },
        }


class SaveContentAction(BaseAction):
    name = "save-content"

    def apply(self, request):
        serializer = SaveContentSerializer(data=request.data)
        if not serializer.is_valid():
            raise ActionRequestException(serializer.errors)
        try:
            post_obj = Post.objects.get(pk=serializer.validated_data["post_id"])
        except Post.DoesNotExist:
            raise BaseActionException("`post_id` is invalid")
        post_obj.content = serializer.validated_data["content"]
        post_obj.save()
        return {
            "success": 1,
            "data": {
                "content": post_obj.content,
                "instance": PostSerializer(post_obj).data,
            },
        }


def get_serializer_class_by_component_type(component_type):
    data_dict = {
        "matching": MatchingComponentCreateUpdateSerializer,
        "question": QuestionComponentSerializer,
        "bluecard": BlueCardComponentSerializer,
        "audio": AudioComponentSerializer,
        "fill-text": FillTextComponentSerializer,
        "video": VideoComponentSerializer,
        "record-audio": RecordingComponentSerializer,
        "order": OrderComponentElementSerializer,
        "image": ImageComponentSerializer,
        "text-pro": TextProComponentSerializer,
    }
    return data_dict.get(component_type, None)


class LoadDemoLessonDataAction(BaseAction):
    name = "load-demo-lesson-data"

    def apply(self, request):
        serializer = BasePostEditSerializer(data=request.data)
        if not serializer.is_valid():
            raise ActionRequestException(serializer.errors)
        try:
            post_obj = Post.objects.get(pk=serializer.validated_data["post_id"])
        except Post.DoesNotExist:
            raise BaseActionException("`post_id` is invalid")
        except Exception as e:
            raise BaseActionException(str(e))
        LessonPageModel = post_obj.content_type.model_class()
        try:
            lesson_page_obj = LessonPageModel.objects.get(pk=post_obj.object_id)
        except LessonPageModel.DoesNotExist:
            raise BaseActionException("`object_id` is invalid")
        except Exception as e:
            raise BaseActionException(str(e))
        lesson_page_serializer = LessonPageSerializer(
            lesson_page_obj,
            context={
                "request": request,
                "user": request.user,
            },
        )
        return {
            "success": 1,
            "data": {
                "lesson_page": lesson_page_serializer.data,
            },
        }


class BuildAndPublishContentAction(BaseAction):
    name = "build-and-publish-content"

    def apply(self, request):
        serializer = BuildAndPublishContentSerializer(data=request.data)
        if not serializer.is_valid():
            raise ActionRequestException(serializer.errors)

        try:
            post_obj = Post.objects.get(pk=serializer.validated_data["post_id"])
        except Post.DoesNotExist:
            raise BaseActionException("`post_id` is invalid")
        except Exception as e:
            raise BaseActionException(str(e))

        if not post_obj.object_id:
            raise BaseActionException("Post object is not set")

        try:
            page_obj = LessonPage.objects.get(pk=post_obj.object_id)
        except LessonPage.DoesNotExist:
            raise BaseActionException(
                "Incorrect connection between Lesson Page and Post Editor object"
            )

        formatted_content = serializer.validated_data["content"].strip()
        try:
            formatted_content = json.loads(formatted_content)
        except json.JSONDecodeError:
            raise BaseActionException("`content` is not a valid JSON string")

        errors = []
        new_formatted_content_data = []
        els_data = []

        # ─────────────────────────────────────────────────────────────────────
        # First pass: Validate blocks structure before mutation
        # ─────────────────────────────────────────────────────────────────────
        for index, block in enumerate(formatted_content.get("blocks", [])):
            block_id = block.get("id")
            data = block.get("data", {})
            obj = data.get("obj")
            i_type = block.get("type")

            if not block_id:
                errors.append(
                    {
                        "block_index": index,
                        "error": "Block must contain `id`",
                        "block": block,
                    }
                )
                continue

            if not obj or "id" not in obj:
                errors.append(
                    {
                        "block_id": block_id,
                        "error": "Object Field is required OR Component does not exist",
                        "block": block,
                    }
                )
                continue

            if not i_type or i_type not in COMPONENT_NAME_TO_COMPONENT_MODEL_CLASS_DICT:
                errors.append(
                    {
                        "block_id": block_id,
                        "error": "`type` is missing or invalid",
                    }
                )
                continue

        if errors:
            raise ActionRequestException(
                "Block-level validation failed before processing components.",
                errors=errors,
            )

        # ─────────────────────────────────────────────────────────────────────
        # Second pass: Process and upsert components and elements
        # ─────────────────────────────────────────────────────────────────────
        for index, i_block in enumerate(formatted_content["blocks"]):
            i_data = i_block["data"]
            i_data_obj = i_data.get("obj")
            i_data_obj_values = i_data.get("values", None)
            i_block_id = i_block.get("id")
            i_type = i_block.get("type")
            i_data_static = i_data.get("static", False)

            component_class = COMPONENT_NAME_TO_COMPONENT_MODEL_CLASS_DICT[i_type]
            field_name = COMPONENT_NAME_TO_ELEMENT_FIELD_NAME_DICT[i_type]
            obj_kwargs = {
                "page": page_obj,
                "order": index + 1,
            }

            # Fetch or create/update component instance
            try:
                component_obj = component_class.objects.get(pk=i_data_obj["id"])
            except component_class.DoesNotExist:
                raise BaseActionException(
                    f"`component_id`={i_data_obj['id']} is invalid"
                )

            if not i_data_static and i_data_obj_values:
                component_serializer = get_serializer_class_by_component_type(i_type)(
                    instance=component_obj, partial=True, data=i_data_obj_values
                )
                if not component_serializer.is_valid():
                    raise ActionRequestException(
                        {
                            "errors": component_serializer.errors,
                            "block_id": i_block_id,
                            "component_type": i_type,
                        }
                    )
                component_obj = component_serializer.save()
                serialized_data = component_serializer.data
            else:
                serialized_data = get_serializer_class_by_component_type(i_type)(
                    instance=component_obj
                ).data

            obj_kwargs[field_name] = component_obj
            used_element_id = i_data.get("element_id")

            content_index = len(new_formatted_content_data)
            els_data.append(
                {
                    "element_id": used_element_id,
                    "page_kwargs": obj_kwargs,
                    "content_index": content_index,
                }
            )

            new_i_ = i_block.copy()
            new_i_["data"]["obj"] = serialized_data
            new_i_["data"]["element_id"] = used_element_id
            new_formatted_content_data.append(new_i_)

        # ─────────────────────────────────────────────────────────────────────
        # Third pass: Upsert LessonPageElements and attach element_ids
        # ─────────────────────────────────────────────────────────────────────
        existing_elements = page_obj.elements.all()
        existing_elements_dict = {i.id: i for i in existing_elements}
        to_keep_ids = []

        for meta in els_data:
            element_id = meta["element_id"]
            page_kwargs = meta["page_kwargs"]
            idx = meta["content_index"]

            if element_id and element_id in existing_elements_dict:
                obj = existing_elements_dict[element_id]
                for key, val in page_kwargs.items():
                    setattr(obj, key, val)
                obj.save()
            else:
                obj = LessonPageElement.objects.create(**page_kwargs)

            element_id = obj.id
            to_keep_ids.append(element_id)
            new_formatted_content_data[idx]["data"]["element_id"] = element_id

        new_formatted_content_data_dict = {
            "date": formatted_content.get("date"),
            "blocks": new_formatted_content_data,
        }

        page_obj.elements.exclude(id__in=to_keep_ids).delete()

        post_obj.content = json.dumps(new_formatted_content_data_dict)
        post_obj.save()

        return {
            "success": 1,
            "data": {
                "instance": PostSerializer(post_obj).data,
                "elements": LessonPageElementSerializer(
                    page_obj.elements.all(), many=True
                ).data,
                "content": post_obj.content,
            },
        }


class LoadContentObjDataAction(BaseAction):
    name = "load-content-obj-data"

    def apply(self, request):
        serializer = LoadComponentObjDataSerializer(data=request.data)
        if not serializer.is_valid():
            raise ActionRequestException(serializer.errors)
        items_data = []
        for i in serializer.validated_data["items"]:
            component_type = i.get("component_type")
            object_id = i.get("object_id")
            component_class = COMPONENT_NAME_TO_COMPONENT_MODEL_CLASS_DICT.get(
                component_type
            )
            if component_class is None:
                raise BaseActionException(
                    f"`component_type` {component_type} is invalid"
                )
            items_data.append(
                {
                    "component_type": component_type,
                    "object_id": object_id,
                    "component_class": component_class,
                }
            )
        items_response_data = []
        for i in items_data:
            component_class = i.get("component_class")
            object_id = i.get("object_id")
            try:
                component_obj = component_class.objects.get(pk=object_id)
            except component_class.DoesNotExist:
                raise BaseActionException("`object_id` is invalid")
            except Exception as e:
                raise BaseActionException(str(e))
            serializer = get_serializer_class_by_component_type(
                i.get("component_type")
            )(component_obj)
            items_response_data.append(
                {
                    "component_type": i.get("component_type"),
                    "object_id": object_id,
                    "component_data": serializer.data,
                }
            )
        return {
            "success": 1,
            "data": {
                "items": items_response_data,
            },
        }


class FileControlAction(BaseAction):
    name = "file-control"

    def apply(self, request):
        serializer = FileControlSerializer(data=request.data)
        if not serializer.is_valid():
            raise ActionRequestException(serializer.errors)
        try:
            post_obj = Post.objects.get(pk=serializer.validated_data["post_id"])
        except Post.DoesNotExist:
            raise ActionRequestException("`post_id` is invalid")
        except Exception as e:
            raise ActionRequestException(str(e))
        file_action_name = serializer.validated_data["file_action"]
        component_name = serializer.validated_data["component_name"]
        file_field_name = serializer.validated_data["file_field_name"]
        component_class = COMPONENT_NAME_TO_COMPONENT_MODEL_CLASS_DICT.get(
            component_name
        )
        if component_class is None:
            raise ActionRequestException(
                f"`component_name` {component_name} is invalid"
            )
        try:
            component_obj = component_class.objects.get(
                pk=serializer.validated_data["object_id"]
            )
        except component_class.DoesNotExist:
            raise ActionRequestException("`object_id` is invalid")
        except Exception as e:
            raise BaseActionException(str(e))
        file_field = getattr(component_obj, file_field_name, None)
        if file_field is None:
            raise ActionRequestException(
                f"`file_field_name` {file_field_name} is invalid for component {component_name}"
            )
        if file_action_name == "upload":
            if file_field:
                file_field.delete(save=False)
            setattr(component_obj, file_field_name, serializer.validated_data["file"])
            component_obj.save()
            return {
                "success": 1,
                "data": {
                    "message": "File uploaded successfully",
                    "component_data": get_serializer_class_by_component_type(
                        component_name
                    )(component_obj).data,
                },
            }
        elif file_action_name == "remove":
            if not file_field:
                raise ActionRequestException(
                    f"No file found for component {component_name} with field {file_field_name}"
                )
            file_field.delete(save=False)
            setattr(component_obj, file_field_name, None)
            component_obj.save()
            return {
                "success": 1,
                "data": {
                    "message": "File removed successfully",
                    "component_data": get_serializer_class_by_component_type(
                        component_name
                    )(component_obj).data,
                },
            }


class ResourcesPostEditContentActionAPIView(BaseApiView):
    available_get_actions = []
    available_post_actions = [
        LoadContentAction(),
        SaveContentAction(),
        LoadDemoLessonDataAction(),
        LoadContentObjDataAction(),
        BuildAndPublishContentAction(),
        FileControlAction(),
        MatchingFileControlAction(),
    ]

    def post(self, request):
        action = request.GET.get("action", None)
        if action is None:
            return Response(
                {"success": 0, "message": "`action` is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        use_action = None
        for i in self.available_post_actions:
            if i.name == action:
                use_action = i
                break
        if use_action is None:
            return Response(
                {"success": 0, "message": "`action` is invalid"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            response = use_action.apply(request)
            return Response(response, status=status.HTTP_200_OK)
        except ActionRequestException as err:
            return Response(
                {
                    "success": 0,
                    "errors": {
                        "message": str(err),
                        "errors": err.errors,
                    },
                }
            )
        except BaseActionException as err:
            return Response({"success": 0, "message": str(err)}, status=err.status)


class ResourcesTextComponentViewSet(BaseApiViewSet):
    search_fields = ["title", "text"]

    def get_queryset(self):
        return TextComponent.objects.all()

    def get_serializer_class(self):
        return TextProComponentSerializer


class ResourcesQuestionComponentViewSet(BaseApiViewSet):
    search_fields = ["text"]

    def get_queryset(self):
        return QuestionComponent.objects.all().prefetch_related("answers")

    def get_serializer_class(self):
        return QuestionComponentSerializer


class ResourcesBlueCardComponentViewSet(BaseApiViewSet):
    search_fields = [
        "text",
    ]

    def get_queryset(self):
        return BlueCardComponent.objects.all()

    def get_serializer_class(self):
        return BlueCardComponentSerializer


class ResourcesAudioComponentViewSet(BaseApiViewSet):
    search_fields = [
        "title",
    ]

    def get_queryset(self):
        return AudioComponent.objects.all()

    def get_serializer_class(self):
        return AudioComponentSerializer


class ResourceFillTextComponentViewSet(BaseApiViewSet):
    search_fields = [
        "title",
    ]

    def get_queryset(self):
        return FillTextComponent.objects.all().prefetch_related("lines")

    def get_serializer_class(self):
        return FillTextComponentSerializer


class ResourcesVideoComponentViewSet(BaseApiViewSet):
    search_fields = [
        "description",
    ]

    def get_queryset(self):
        return VideoComponent.objects.all()

    def get_serializer_class(self):
        return VideoComponentSerializer


class ResourcesOrderComponentViewSet(BaseApiViewSet):
    search_fields = [
        "title",
    ]

    def get_queryset(self):
        return PutInOrderComponent.objects.all().prefetch_related("elements")

    def get_serializer_class(self):
        return OrderComponentElementSerializer


class ResourcesRecordAudioComponentViewSet(BaseApiViewSet):
    search_fields = [
        "title",
        "description",
    ]

    def get_queryset(self):
        return RecordAudioComponent.objects.all()

    def get_serializer_class(self):
        return RecordingComponentSerializer


class ResourcesImageComponentViewSet(BaseApiViewSet):
    search_fields = [
        "description",
    ]

    def get_queryset(self):
        return ImageComponent.objects.all()

    def get_serializer_class(self):
        return ImageComponentSerializer


__ALL__ = [
    "ResourcesTextComponentViewSet",
    "ResourcesQuestionComponentViewSet",
    "ResourcesBlueCardComponentViewSet",
    "ResourcesAudioComponentViewSet",
    "ResourceFillTextComponentViewSet",
    "ResourcesVideoComponentViewSet",
    "ResourcesOrderComponentViewSet",
    "ResourcesRecordAudioComponentViewSet",
    "ResourcesImageComponentViewSet",
    "ResourcesPostEditContentActionAPIView",
    MatchingComponentViewSet,
]

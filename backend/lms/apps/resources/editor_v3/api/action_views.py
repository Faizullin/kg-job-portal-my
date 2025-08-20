from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.response import Response

from api_lessons.models import LessonPage
from lms.apps.core.models import PublicationStatus
from lms.apps.core.utils.api_actions import (
    BaseAction,
    BaseActionException,
    ActionRequestException,
)
from lms.apps.core.utils.crud_base.views import BaseApiView
from lms.apps.posts.models import Post
from .serializers import (
    BasePostEditSerializer,
    PublishContentSerializer,
    PostSerializer,
    SaveContentSerializer,
)


class EditorPostActionBase(BaseAction):
    def validate_serializer(
        self, request, serializer_class=BasePostEditSerializer, use_post_query=True
    ):
        serializer = serializer_class(data=request.data)
        if not serializer.is_valid():
            raise ActionRequestException(serializer.errors)
        return serializer

    def validate_and_get_post(self, post_id) -> Post:
        try:
            post_obj = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            raise BaseActionException("`post_id` is invalid")
        except Exception as e:
            raise BaseActionException(str(e))
        if post_obj.post_type != "editor3":
            raise BaseActionException(
                "`post_id` does not refer to a valid post for the editor"
            )
        return post_obj

    def validate_and_get_page(self, post_obj: Post) -> LessonPage:
        lesson_page_model = post_obj.content_type.model_class()
        if lesson_page_model != LessonPage:
            raise BaseActionException(
                "`content_type` does not refer to a valid lesson page model"
            )
        try:
            page_obj = LessonPage.objects.get(pk=post_obj.object_id)
        except LessonPage.DoesNotExist:
            raise BaseActionException("`object_id` is invalid")
        except Exception as e:
            raise BaseActionException(str(e))
        return page_obj


class LoadContentAction(EditorPostActionBase):
    name = "load-content"

    def apply(self, request):
        serializer = self.validate_serializer(request)
        post_obj = self.validate_and_get_post(serializer.validated_data["post_id"])
        page_obj = self.validate_and_get_page(post_obj)
        json_instance_data = PostSerializer(post_obj).data
        json_instance_data["content_type"] = page_obj._meta.model_name
        json_instance_data["object_id"] = post_obj.object_id
        return {
            "success": 1,
            "data": {
                "message": "Content loaded successfully",
                "content": post_obj.content,
                "instance": json_instance_data,
            },
        }


class SaveContentAction(EditorPostActionBase):
    name = "save-content"

    def apply(self, request):
        serializer = self.validate_serializer(
            request, serializer_class=SaveContentSerializer
        )
        post_obj = self.validate_and_get_post(serializer.validated_data["post_id"])
        page_obj = self.validate_and_get_page(post_obj)
        post_obj.content = serializer.validated_data["content"]
        post_obj.save()
        json_instance_data = PostSerializer(post_obj).data
        json_instance_data["content_type"] = page_obj._meta.model_name
        json_instance_data["object_id"] = post_obj.object_id
        return {
            "success": 1,
            "data": {
                "message": "Content saved successfully",
                "content": post_obj.content,
                "instance": json_instance_data,
            },
        }


class PublishContentAction(EditorPostActionBase):
    name = "publish-content"

    def apply(self, request):
        serializer = self.validate_serializer(
            request, serializer_class=PublishContentSerializer
        )
        post_obj = self.validate_and_get_post(serializer.validated_data["post_id"])
        page_obj = self.validate_and_get_page(post_obj)
        post_obj.publication_status = serializer.validated_data["publication_status"]
        post_obj.save()
        ct = ContentType.objects.get_for_model(LessonPage)
        lesson_page_public_post_obj, created = Post.objects.get_or_create(
            slug = f"{post_obj.slug}-public",
            content_type=ct,
            object_id=page_obj.pk,
            post_type="lesson-page-public",
            defaults={
                "title": post_obj.title,
                "author": post_obj.author,
                "category": post_obj.category,
                "publication_status": post_obj.publication_status,
                "content": post_obj.content,
            },
        )
        lesson_page_public_post_obj.content = post_obj.content
        lesson_page_public_post_obj.title = post_obj.title
        lesson_page_public_post_obj.save()
        return {
            "success": 1,
            "data": {
                "message": "Content built and published successfully",
                "instance": PostSerializer(post_obj).data,
                "content": post_obj.content,
            },
        }


class LoadDemoLessonDataAction(EditorPostActionBase):
    name = "load-demo-lesson-data"

    def apply(self, request):
        # TODO: Implement the logic to load demo lesson data
        serializer = self.validate_serializer(request)
        post_obj = self.validate_and_get_post(serializer.validated_data["post_id"])
        page_obj = self.validate_and_get_page(post_obj)
        lesson_page_data = {
            "id": page_obj.pk,
            "order": page_obj.order,
            "title": page_obj.title,
            "content": post_obj.content,
        }
        return {
            "success": 1,
            "data": {
                "message": "Demo lesson data loaded successfully",
                "lesson_page": lesson_page_data,
            },
        }


class DestroyPostEditorAction(EditorPostActionBase):
    name = "destroy-post-editor"

    def apply(self, request):
        serializer = self.validate_serializer(request)
        post_obj = self.validate_and_get_post(serializer.validated_data["post_id"])
        self.validate_and_get_page(post_obj)
        if post_obj.publication_status == PublicationStatus.PUBLISH:
            raise BaseActionException(
                "Cannot delete a published post. Please unpublish it first."
            )
        if post_obj.author != request.user:
            raise BaseActionException("You do not have permission to delete this post.")
        try:
            post_obj = Post.objects.get(
                content_type=post_obj._meta.model_name,
                object_id=post_obj.pk,
                post_type="lesson-page-public",
            )
            post_obj.publication_status = PublicationStatus.DRAFT
            post_obj.save()
        except Post.DoesNotExist:
            pass
        post_obj.delete()
        return {
            "success": 1,
            "data": {
                "message": "Editor Post Post deleted successfully",
            },
        }


class ResourcesLessonEditActionAPIView(BaseApiView):
    available_post_actions = [
        LoadContentAction(),
        SaveContentAction(),
        LoadDemoLessonDataAction(),
        PublishContentAction(),
        DestroyPostEditorAction(),
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

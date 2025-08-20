from django_filters import CharFilter
from django_filters.rest_framework import FilterSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from lms.apps.core.models import PublicationStatus
from lms.apps.core.utils.crud_base.views import BaseListApiView, BaseApiViewSet
from lms.apps.posts.models import Post, Tag, Category
from .serializers import (
    PostSerializer,
    TagSerializer,
    PostSubmitSerializer,
    CategorySerializer,
)


class ResourcesPostViewSet(BaseApiViewSet):
    search_fields = [
        "title",
    ]

    class PostFilter(FilterSet):
        title = CharFilter(lookup_expr="icontains")
        post_type = CharFilter(lookup_expr="icontains")

        class Meta:
            model = Post
            fields = ["id", "title", "author", "publication_status", "post_type"]

    filterset_class = PostFilter

    def get_queryset(self):
        return Post.objects.all().prefetch_related("author", "category", "thumbnail")

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ["POST", "PUT", "PATCH"]:
            return PostSubmitSerializer
        return PostSerializer

    @action(
        detail=True,
        methods=["post"],
    )
    def publish(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        self.check_object_permissions(request, post)
        post.publication_status = PublicationStatus.PUBLISH
        post.save()
        return Response(
            {"detail": "Post published successfully"}, status=status.HTTP_200_OK
        )


class TagListAPIView(BaseListApiView):
    serializer_class = TagSerializer
    search_fields = ["title"]

    def get_queryset(self):
        queryset = Tag.objects.all()
        return queryset


class ResourcesCategoryViewSet(BaseApiViewSet):
    search_fields = ["title"]

    def get_queryset(self):
        return Category.objects.all()

    def get_serializer_class(self):
        return CategorySerializer

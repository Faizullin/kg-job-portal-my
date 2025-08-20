from django_filters import CharFilter, NumberFilter
from django_filters.rest_framework import FilterSet
from rest_framework import serializers

from lms.apps.comments.models import Comment
from lms.apps.core.utils.crud_base.views import BaseApiViewSet


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            'id',
            'content_type',
            'object_id',
            'user',
            'user_name',
            'parent',
            'text',
            'meta_term',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CommentViewSet(BaseApiViewSet):
    search_fields = ['user_name', ]
    ordering_fields = ['id', ]
    ordering = ['-id']

    class CommentFilter(FilterSet):
        content_type = CharFilter(field_name='content_type__model', lookup_expr='exact')
        object_id = NumberFilter(field_name='object_id', lookup_expr='exact')

        class Meta:
            model = Comment
            fields = ['*']

    filterset_class = CommentFilter

    def get_queryset(self):
        return Comment.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CommentSerializer
        return CommentSerializer

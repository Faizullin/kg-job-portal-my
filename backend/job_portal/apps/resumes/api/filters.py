from django_filters import rest_framework as filters

from job_portal.apps.resumes.models import ResumeStatus, MasterResume


class ResumeFilter(filters.FilterSet):
    """Filter set for resume searches"""

    status = filters.ChoiceFilter(choices=ResumeStatus.choices)
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    updated_after = filters.DateTimeFilter(field_name='updated_at', lookup_expr='gte')
    updated_before = filters.DateTimeFilter(field_name='updated_at', lookup_expr='lte')
    title_contains = filters.CharFilter(field_name='title', lookup_expr='icontains')
    content_contains = filters.CharFilter(field_name='content', lookup_expr='icontains')

    class Meta:
        model = MasterResume
        fields = [
            'status', 'created_after', 'created_before',
            'updated_after', 'updated_before', 'title_contains',
            'content_contains'
        ]

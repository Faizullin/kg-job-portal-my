import django_filters
from django.core.exceptions import ValidationError

from ..models import JobApplication, Job, JobStatus, JobApplicationStatus, JobUrgency


class JobApplicationFilter(django_filters.FilterSet):
    job_id = django_filters.NumberFilter(field_name='job__id', method='filter_by_job_id')
    status = django_filters.ChoiceFilter(choices=JobApplicationStatus.choices)
    job__service_subcategory = django_filters.NumberFilter(field_name='job__service_subcategory__id')
    job__urgency = django_filters.ChoiceFilter(field_name='job__urgency', choices=JobUrgency.choices)
    applied_at = django_filters.DateFromToRangeFilter()
    amount_min = django_filters.NumberFilter(field_name='amount', lookup_expr='gte')
    amount_max = django_filters.NumberFilter(field_name='amount', lookup_expr='lte')

    class Meta:
        model = JobApplication
        fields = ['status', 'job_id', 'job__service_subcategory', 'job__urgency', 'applied_at', 'amount_min',
                  'amount_max']

    def filter_by_job_id(self, queryset, name, value):
        if not value:
            return queryset

        try:
            job = Job.objects.get(id=value, status=JobStatus.PUBLISHED)
            return queryset.filter(job=job)
        except Job.DoesNotExist:
            raise ValidationError(f"Job with ID {value} does not exist")
        except ValueError:
            raise ValidationError(f"Invalid job ID: {value}")

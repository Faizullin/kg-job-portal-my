import django_filters
from django.core.exceptions import ValidationError

from ..models import JobApplication, Job, JobStatus, JobApplicationStatus, JobUrgency


class JobFilter(django_filters.FilterSet):
    """Filter for Job model with master dashboard support."""
    
    # Price filtering
    min_price = django_filters.NumberFilter(field_name='budget_min', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='budget_max', lookup_expr='lte')
    
    # Service filtering
    service_subcategory = django_filters.NumberFilter(field_name='service_subcategory__id')
    service_category = django_filters.NumberFilter(field_name='service_subcategory__category__id')
    
    # Location filtering
    city = django_filters.CharFilter(field_name='city__name', lookup_expr='icontains')
    
    # Time filtering
    service_date_from = django_filters.DateFilter(field_name='service_date', lookup_expr='gte')
    service_date_to = django_filters.DateFilter(field_name='service_date', lookup_expr='lte')
    
    # Urgency filtering
    urgency = django_filters.ChoiceFilter(choices=JobUrgency.choices)
    
    class Meta:
        model = Job
        fields = [
            'min_price', 'max_price', 'service_subcategory', 'service_category',
            'city', 'service_date_from', 'service_date_to', 'urgency'
        ]


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

from django.urls import path
from .api.views import MasterSearchAPIView, JobSearchAPIView

app_name = 'search'

urlpatterns = [
    path('api/v1/search/masters/', MasterSearchAPIView.as_view(), name='master-search'),
    path('api/v1/search/jobs/', JobSearchAPIView.as_view(), name='job-search'),
]

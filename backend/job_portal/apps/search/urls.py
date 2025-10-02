from django.urls import path
from .api.views import (
    MasterSearchAPIView,
    JobSearchAPIView,
    HomeClientAPIView,
    MasterRecommendedJobsAPIView
)

app_name = 'search'

urlpatterns = [
    path('api/v1/search/masters/', MasterSearchAPIView.as_view(), name='master-search'),
    path('api/v1/search/jobs/', JobSearchAPIView.as_view(), name='job-search'),
    
    # Master recommendation system for employers
    path('api/v1/home/client', HomeClientAPIView.as_view(), name='master-recommendations'),
    path('api/v1/home/master/new-jobs/', MasterRecommendedJobsAPIView.as_view(), name='master-new-jobs'),
]

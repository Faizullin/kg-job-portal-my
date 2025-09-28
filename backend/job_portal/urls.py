from django.urls import path, include

app_name = 'job_portal'

urlpatterns = [
    path('', include('job_portal.apps.core.urls')),
    path('', include('job_portal.apps.jobs.urls')),
    path('', include('job_portal.apps.users.urls')),
    path('', include('job_portal.apps.resumes.urls')),
    path('', include('job_portal.apps.chats.urls')),
    path('', include('job_portal.apps.notifications.urls')),
    # path('', include('job_portal.apps.reviews.urls')),
]

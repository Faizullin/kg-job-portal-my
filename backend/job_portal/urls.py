from django.urls import path, include

app_name = 'job_portal'

urlpatterns = [
    # Include all app URLs so Flutter app can access them
    path('', include('job_portal.apps.core.urls')),
    path('', include('job_portal.apps.users.urls')),
    path('', include('job_portal.apps.orders.urls')),
    path('', include('job_portal.apps.payments.urls')),
    path('', include('job_portal.apps.chat.urls')),
    path('', include('job_portal.apps.notifications.urls')),
    path('', include('job_portal.apps.analytics.urls')),
]

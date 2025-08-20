"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([])
        ),  # Add routes here
    ),
})

# # -----------------------------NECESSARY SCHEDULING----------------------------------------------------------
# from django_q.tasks import schedule
# from django_q.models import Schedule

# # Check if the task exists
# if Schedule.objects.filter(name='check_for_strike').exists():
#     print("check_for_strike already exists, skipping creation...")
# else:
#     from django.utils import timezone

#     schedule(
#         'api_users.tasks.check_for_strike',
#         name='check_for_strike',
#         schedule_type=Schedule.MINUTES,
#         minutes=60,
#         repeats=-1,
#         next_run=timezone.now() + timezone.timedelta(minutes=1),
#     )

#     print('started admin_farm_check task!')

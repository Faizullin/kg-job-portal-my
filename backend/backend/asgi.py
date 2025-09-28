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
from job_portal.apps.chats.routing import websocket_urlpatterns
from job_portal.apps.chats.middleware import JWTWebSocketAuthMiddleware

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket":
        # AllowedHostsOriginValidator(
            JWTWebSocketAuthMiddleware(
                AuthMiddlewareStack(
                    URLRouter(websocket_urlpatterns)
                )
            ),
        # ),

})

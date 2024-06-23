import os
from channels.routing import ProtocolTypeRouter, URLRouter
from myapp import routing
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

application = ProtocolTypeRouter(

    {

        "http" : get_asgi_application(),
        "websocket" : AuthMiddlewareStack(

            URLRouter(
                routing.websocket_urlpatterns
            )

        )
    }
)

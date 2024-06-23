from django.urls import path, include
from myapp.consumer import ChatConsumer, PrivateChatConsumer

websocket_urlpatterns = [

    path("ws/chat/", ChatConsumer.as_asgi()),
    path('ws/private-chat/', PrivateChatConsumer.as_asgi())

]
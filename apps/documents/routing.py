from django.urls import re_path

from apps.documents.consumers import DocumentNotificationConsumer

websocket_urlpatterns = [
    re_path(r"^ws/documents/$", DocumentNotificationConsumer.as_asgi()),
]

import json

from channels.generic.websocket import AsyncWebsocketConsumer


class DocumentNotificationConsumer(AsyncWebsocketConsumer):
    """Broadcasts document create/update events to every connected,
    authenticated client. Clients connect to ``/ws/documents/``.
    """

    GROUP_NAME = "documents"

    async def connect(self):
        if not self.scope["user"] or not self.scope["user"].is_authenticated:
            await self.close(code=4001)
            return

        await self.channel_layer.group_add(self.GROUP_NAME, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.GROUP_NAME, self.channel_name)

    async def document_notification(self, event):
        await self.send(text_data=json.dumps({
            "event": event["event"],
            "document_id": event["document_id"],
            "title": event["title"],
        }))

import logging

from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer

logger = logging.getLogger("apps.documents")


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def process_document(self, document_id: str) -> None:
    """Background post-processing for an uploaded document.

    This is intentionally decoupled from the request/response cycle so
    uploads respond quickly. In a real system this might do things like
    virus scanning, thumbnail generation, or text extraction for search
    indexing; here it demonstrates the pattern and flips the
    ``is_processed`` flag once "processing" completes.
    """
    from apps.documents.models import Document  # local import avoids app-loading issues

    try:
        document = Document.objects.get(id=document_id)
    except Document.DoesNotExist:
        logger.warning("process_document: document %s no longer exists", document_id)
        return

    logger.info("Processing document %s (%s)", document.id, document.title)

    # Placeholder for real processing (virus scan / thumbnailing / OCR / etc).
    document.is_processed = True
    document.save(update_fields=["is_processed", "updated_at"])

    _notify_websocket_clients(document, event="document_processed")


def _notify_websocket_clients(document, event: str) -> None:
    """Push a real-time notification to the 'documents' broadcast group
    over WebSocket via Django Channels, so connected clients learn about
    new/updated documents without polling.
    """
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    async_to_sync(channel_layer.group_send)(
        "documents",
        {
            "type": "document.notification",
            "event": event,
            "document_id": str(document.id),
            "title": document.title,
        },
    )

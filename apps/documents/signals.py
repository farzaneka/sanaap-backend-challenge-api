from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.documents.models import Document


def _current_user():
    """Best-effort retrieval of the user performing the change.

    Django signals don't receive the request by default. We rely on
    ``Document.save()``/``delete()`` being called from within a request
    handled by DRF, where ``perform_create``/``perform_update`` already
    set ``instance.owner``; for a fuller solution a request-scoped
    threadlocal (e.g. via django-crum) could capture the *acting* user
    distinctly from the document owner. Kept simple here for clarity.
    """
    return None


@receiver(post_save, sender=Document)
def log_document_save(sender, instance: Document, created: bool, **kwargs) -> None:
    from apps.audit.models import AuditAction, AuditLog

    AuditLog.objects.create(
        user=instance.owner,
        action=AuditAction.CREATE if created else AuditAction.UPDATE,
        resource="Document",
        resource_id=str(instance.id),
        metadata={"title": instance.title, "size": instance.size},
    )


@receiver(post_delete, sender=Document)
def log_document_delete(sender, instance: Document, **kwargs) -> None:
    from apps.audit.models import AuditAction, AuditLog

    AuditLog.objects.create(
        user=instance.owner,
        action=AuditAction.DELETE,
        resource="Document",
        resource_id=str(instance.id),
        metadata={"title": instance.title},
    )

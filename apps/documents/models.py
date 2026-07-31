import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


def validate_file_size(file) -> None:
    max_size = settings.MAX_UPLOAD_SIZE_BYTES
    if file.size > max_size:
        raise ValidationError(
            f"File too large. Max size is {max_size // (1024 * 1024)} MB."
        )


def validate_content_type(file) -> None:
    content_type = getattr(file, "content_type", None)
    allowed = settings.ALLOWED_UPLOAD_CONTENT_TYPES
    if content_type and content_type not in allowed:
        raise ValidationError(
            f"Unsupported file type '{content_type}'. Allowed types: {', '.join(allowed)}"
        )


def document_upload_path(instance: "Document", filename: str) -> str:
    """Namespaced, unguessable storage path.

    Using the document's own UUID (instead of the original filename)
    prevents filename collisions and stops users from being able to guess
    other users' object keys.
    """
    ext = filename.rsplit(".", 1)[-1] if "." in filename else ""
    safe_name = f"{instance.id}.{ext}" if ext else str(instance.id)
    return f"{instance.owner_id}/{safe_name}"


class Document(models.Model):
    """A single uploaded document/file and its metadata."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    file = models.FileField(
        upload_to=document_upload_path,
        validators=[validate_file_size, validate_content_type],
    )
    content_type = models.CharField(max_length=150, blank=True)
    size = models.PositiveBigIntegerField(default=0, help_text="File size in bytes.")
    checksum = models.CharField(max_length=64, blank=True, help_text="SHA-256 hash of the file content.")

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="documents",
        on_delete=models.CASCADE,
    )

    tags = models.CharField(
        max_length=255, blank=True, default="",
        help_text="Comma separated tags, used for filtering.",
    )

    is_processed = models.BooleanField(
        default=False,
        help_text="Set to True once the background processing task has finished.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "documents"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["owner", "-created_at"]),
            models.Index(fields=["content_type"]),
        ]

    def __str__(self) -> str:
        return self.title

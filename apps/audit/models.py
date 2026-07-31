from django.conf import settings
from django.db import models


class AuditAction(models.TextChoices):
    VIEW = "view", "View"
    CREATE = "create", "Create"
    UPDATE = "update", "Update"
    DELETE = "delete", "Delete"
    LOGIN = "login", "Login"
    REQUEST = "request", "Request"


class AuditLog(models.Model):
    """Immutable record of who did what, and when, for compliance /
    traceability. Populated both by explicit signals (document
    create/update/delete) and by a lightweight middleware that records
    every authenticated API request.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="audit_logs",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    action = models.CharField(max_length=20, choices=AuditAction.choices)
    resource = models.CharField(max_length=100, help_text="e.g. 'Document', or the request path.")
    resource_id = models.CharField(max_length=100, blank=True, default="")
    method = models.CharField(max_length=10, blank=True, default="")
    path = models.CharField(max_length=500, blank=True, default="")
    status_code = models.PositiveSmallIntegerField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "audit_logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["resource", "resource_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.user} {self.action} {self.resource}:{self.resource_id}"

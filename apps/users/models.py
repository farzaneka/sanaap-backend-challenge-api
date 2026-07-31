from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    """The three roles supported by the RBAC system.

    - ADMIN: full access - create users, assign roles, manage all documents.
    - EDITOR: can upload and update documents, but cannot delete them.
    - VIEWER: read-only access to documents.
    """
    ADMIN = "admin", "Admin"
    EDITOR = "editor", "Editor"
    VIEWER = "viewer", "Viewer"


class User(AbstractUser):
    """Custom user model that extends Django's built-in auth user with a
    ``role`` field used for Role Based Access Control (RBAC).

    We extend AbstractUser (instead of writing a fully custom model) so we
    keep Django's battle-tested username/password authentication, password
    hashing, and admin integration "for free", per the requirement to use
    Django's built-in auth for login.
    """

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.VIEWER,
        help_text="Determines what actions the user is allowed to perform on documents.",
    )

    class Meta:
        db_table = "users"

    def __str__(self) -> str:
        return f"{self.username} ({self.role})"

    @property
    def is_admin_role(self) -> bool:
        return self.role == Role.ADMIN

    @property
    def is_editor_role(self) -> bool:
        return self.role == Role.EDITOR

    @property
    def is_viewer_role(self) -> bool:
        return self.role == Role.VIEWER

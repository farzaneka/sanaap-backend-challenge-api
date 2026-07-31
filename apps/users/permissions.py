"""
Role Based Access Control (RBAC) permission classes.

These are intentionally kept generic/reusable (Single Responsibility +
Open/Closed from SOLID) so both the ``users`` and ``documents`` apps can
compose them as needed instead of duplicating role-checking logic.
"""

from rest_framework.permissions import BasePermission

from apps.users.models import Role


class IsAdmin(BasePermission):
    """Grants access only to users with the ``admin`` role."""

    message = "Only administrators are allowed to perform this action."

    def has_permission(self, request, view) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == Role.ADMIN
        )


class IsAdminOrReadOnlyForOthers(BasePermission):
    """Everyone authenticated can read (list/retrieve); only admins can write."""

    def has_permission(self, request, view) -> bool:
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return request.user.role == Role.ADMIN

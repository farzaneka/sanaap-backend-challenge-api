"""
RBAC permission rules specific to the Document resource.

Rules (per spec):
- admin:  full access to all documents (create, update, delete, view)
- editor: can upload (create) and update documents, but cannot delete
- viewer: can only retrieve/list documents
"""

from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.users.models import Role


class DocumentPermission(BasePermission):
    """Object level + view level permission for the Document resource."""

    def has_permission(self, request, view) -> bool:
        if not (request.user and request.user.is_authenticated):
            return False

        role = request.user.role

        if request.method in SAFE_METHODS:
            # admin, editor, viewer can all read
            return role in (Role.ADMIN, Role.EDITOR, Role.VIEWER)

        if request.method == "POST":
            # only admin and editor can upload new documents
            return role in (Role.ADMIN, Role.EDITOR)

        if request.method in ("PUT", "PATCH"):
            # only admin and editor can update
            return role in (Role.ADMIN, Role.EDITOR)

        if request.method == "DELETE":
            # only admin can delete
            return role == Role.ADMIN

        return False

    def has_object_permission(self, request, view, obj) -> bool:
        role = request.user.role

        if request.method in SAFE_METHODS:
            return True

        if role == Role.ADMIN:
            return True

        if role == Role.EDITOR:
            # editors may update any document but never delete
            if request.method == "DELETE":
                return False
            return True

        return False

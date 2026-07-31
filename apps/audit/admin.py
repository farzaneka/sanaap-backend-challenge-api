from django.contrib import admin

from apps.audit.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "action", "resource", "resource_id", "status_code", "ip_address")
    list_filter = ("action", "resource")
    search_fields = ("resource_id", "path", "user__username")
    readonly_fields = [f.name for f in AuditLog._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        # Audit logs must remain immutable; only superusers may prune old
        # records directly via the database/admin if legally required.
        return request.user.is_superuser

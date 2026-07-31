"""
Lightweight middleware that records every authenticated API request as an
audit log entry - satisfies the "Audit Logging for document access and
changes" bonus requirement at the transport level, complementing the
model-level signals in apps/documents/signals.py which capture *what*
changed.
"""


class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        self._log_request(request, response)
        return response

    @staticmethod
    def _log_request(request, response) -> None:
        if not request.path.startswith("/api/"):
            return

        user = getattr(request, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            return

        # Imported lazily to avoid touching the DB / app registry at
        # import time, and to keep this middleware fast for excluded paths.
        from apps.audit.models import AuditAction, AuditLog

        action_map = {
            "GET": AuditAction.VIEW,
            "POST": AuditAction.CREATE,
            "PUT": AuditAction.UPDATE,
            "PATCH": AuditAction.UPDATE,
            "DELETE": AuditAction.DELETE,
        }

        AuditLog.objects.create(
            user=user,
            action=action_map.get(request.method, AuditAction.REQUEST),
            resource="http_request",
            method=request.method,
            path=request.path,
            status_code=getattr(response, "status_code", None),
            ip_address=_client_ip(request),
        )


def _client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")

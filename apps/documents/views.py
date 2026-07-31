from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.parsers import FormParser, MultiPartParser

from apps.documents.filters import DocumentFilter
from apps.documents.models import Document
from apps.documents.permissions import DocumentPermission
from apps.documents.serializers import DocumentSerializer
from apps.documents.tasks import process_document
from apps.users.models import Role


class DocumentViewSet(viewsets.ModelViewSet):
    """CRUD endpoint for documents.

    - list/retrieve: admin, editor, viewer
    - create/update: admin, editor
    - delete: admin only

    Filtering (django-filter) and pagination (DRF's PageNumberPagination,
    configured globally in settings) are enabled by default.
    """

    serializer_class = DocumentSerializer
    permission_classes = [DocumentPermission]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DocumentFilter
    search_fields = ["title", "description", "tags"]
    ordering_fields = ["created_at", "updated_at", "title", "size"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Viewers/editors only see their own documents unless they are
        admins, who can see (and manage) everything. Adjust here if the
        business rule is "everyone sees everything" -- kept role-scoped
        by default for stronger data isolation.
        """
        user = self.request.user
        queryset = Document.objects.select_related("owner").all()
        if user.role == Role.ADMIN:
            return queryset
        return queryset.filter(owner=user)

    def perform_create(self, serializer):
        document = serializer.save()
        process_document.delay(str(document.id))

    def perform_update(self, serializer):
        document = serializer.save()
        if "file" in self.request.data:
            process_document.delay(str(document.id))

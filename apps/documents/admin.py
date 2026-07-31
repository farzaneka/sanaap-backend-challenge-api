from django.contrib import admin

from apps.documents.models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "content_type", "size", "is_processed", "created_at")
    list_filter = ("content_type", "is_processed", "created_at")
    search_fields = ("title", "description", "tags")
    readonly_fields = ("id", "checksum", "size", "created_at", "updated_at")

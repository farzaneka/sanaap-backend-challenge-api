import hashlib

from rest_framework import serializers

from apps.documents.models import Document


class DocumentSerializer(serializers.ModelSerializer):
    """Full document representation, including a secure (presigned)
    download URL rather than exposing the raw storage path.
    """

    download_url = serializers.SerializerMethodField()
    owner_username = serializers.CharField(source="owner.username", read_only=True)

    class Meta:
        model = Document
        fields = (
            "id", "title", "description", "file", "download_url",
            "content_type", "size", "checksum", "tags",
            "owner", "owner_username", "is_processed",
            "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "content_type", "size", "checksum", "owner",
            "is_processed", "created_at", "updated_at", "download_url",
        )
        extra_kwargs = {"file": {"write_only": True}}

    def get_download_url(self, obj: Document) -> str | None:
        if not obj.file:
            return None
        request = self.context.get("request")
        url = obj.file.url  # MinioMediaStorage returns a presigned, expiring URL
        return request.build_absolute_uri(url) if request else url

    def create(self, validated_data):
        request = self.context["request"]
        uploaded_file = validated_data["file"]

        validated_data["owner"] = request.user
        validated_data["content_type"] = getattr(uploaded_file, "content_type", "") or ""
        validated_data["size"] = uploaded_file.size
        validated_data["checksum"] = self._compute_checksum(uploaded_file)

        return super().create(validated_data)

    def update(self, instance, validated_data):
        uploaded_file = validated_data.get("file")
        if uploaded_file is not None:
            validated_data["content_type"] = getattr(uploaded_file, "content_type", "") or ""
            validated_data["size"] = uploaded_file.size
            validated_data["checksum"] = self._compute_checksum(uploaded_file)
            validated_data["is_processed"] = False  # re-trigger processing on update

        return super().update(instance, validated_data)

    @staticmethod
    def _compute_checksum(uploaded_file) -> str:
        hasher = hashlib.sha256()
        for chunk in uploaded_file.chunks():
            hasher.update(chunk)
        uploaded_file.seek(0)
        return hasher.hexdigest()

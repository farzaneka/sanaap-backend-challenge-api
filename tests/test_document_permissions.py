import io

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from tests.factories import AdminUserFactory, DocumentFactory, EditorUserFactory, ViewerUserFactory


def _upload_file(name="test.txt", content=b"hello world", content_type="text/plain"):
    from django.core.files.uploadedfile import SimpleUploadedFile
    return SimpleUploadedFile(name, content, content_type=content_type)


@pytest.mark.django_db
class TestDocumentRBAC:
    def setup_method(self):
        self.client = APIClient()
        self.list_url = reverse("document-list")

    def test_viewer_can_list_own_documents(self):
        viewer = ViewerUserFactory()
        DocumentFactory(owner=viewer)
        self.client.force_authenticate(viewer)

        response = self.client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_viewer_cannot_upload_document(self):
        viewer = ViewerUserFactory()
        self.client.force_authenticate(viewer)

        response = self.client.post(
            self.list_url,
            {"title": "New doc", "file": _upload_file()},
            format="multipart",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_editor_can_upload_document(self):
        editor = EditorUserFactory()
        self.client.force_authenticate(editor)

        response = self.client.post(
            self.list_url,
            {"title": "New doc", "file": _upload_file()},
            format="multipart",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "New doc"

    def test_editor_can_update_document(self):
        editor = EditorUserFactory()
        document = DocumentFactory(owner=editor)
        self.client.force_authenticate(editor)
        detail_url = reverse("document-detail", args=[document.id])

        response = self.client.patch(detail_url, {"title": "Updated title"}, format="multipart")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Updated title"

    def test_editor_cannot_delete_document(self):
        editor = EditorUserFactory()
        document = DocumentFactory(owner=editor)
        self.client.force_authenticate(editor)
        detail_url = reverse("document-detail", args=[document.id])

        response = self.client.delete(detail_url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_delete_document(self):
        admin = AdminUserFactory()
        document = DocumentFactory(owner=admin)
        self.client.force_authenticate(admin)
        detail_url = reverse("document-detail", args=[document.id])

        response = self.client.delete(detail_url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_admin_sees_all_documents_not_just_own(self):
        admin = AdminUserFactory()
        other_viewer = ViewerUserFactory()
        DocumentFactory(owner=other_viewer)
        DocumentFactory(owner=admin)
        self.client.force_authenticate(admin)

        response = self.client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2

    def test_viewer_cannot_see_other_users_documents(self):
        viewer = ViewerUserFactory()
        other_viewer = ViewerUserFactory()
        DocumentFactory(owner=other_viewer)
        self.client.force_authenticate(viewer)

        response = self.client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0

    def test_unauthenticated_request_is_rejected(self):
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

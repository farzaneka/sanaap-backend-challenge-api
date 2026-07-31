import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from tests.factories import AdminUserFactory, DocumentFactory


@pytest.mark.django_db
class TestDocumentFilteringAndPagination:
    def setup_method(self):
        self.client = APIClient()
        self.admin = AdminUserFactory()
        self.client.force_authenticate(self.admin)
        self.list_url = reverse("document-list")

    def test_filter_by_title(self):
        DocumentFactory(owner=self.admin, title="Invoice March")
        DocumentFactory(owner=self.admin, title="Contract Draft")

        response = self.client.get(self.list_url, {"title": "invoice"})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["title"] == "Invoice March"

    def test_filter_by_content_type(self):
        DocumentFactory(owner=self.admin, content_type="application/pdf")
        DocumentFactory(owner=self.admin, content_type="text/plain")

        response = self.client.get(self.list_url, {"content_type": "application/pdf"})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_pagination_default_page_size(self):
        for i in range(15):
            DocumentFactory(owner=self.admin, title=f"Doc {i}")

        response = self.client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 10  # PAGE_SIZE from settings
        assert response.data["next"] is not None

    def test_search_across_title_and_description(self):
        DocumentFactory(owner=self.admin, title="Random", description="quarterly financial report")
        DocumentFactory(owner=self.admin, title="Other", description="unrelated content")

        response = self.client.get(self.list_url, {"search": "financial"})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

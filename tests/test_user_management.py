import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from tests.factories import AdminUserFactory, ViewerUserFactory
from apps.users.models import Role


@pytest.mark.django_db
class TestUserManagementRBAC:
    def setup_method(self):
        self.client = APIClient()
        self.list_url = reverse("user-list-create")

    def test_admin_can_create_user(self):
        admin = AdminUserFactory()
        self.client.force_authenticate(admin)

        response = self.client.post(self.list_url, {
            "username": "newbie",
            "email": "newbie@example.com",
            "password": "supersecret123",
            "role": Role.EDITOR,
        })

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["role"] == Role.EDITOR

    def test_non_admin_cannot_create_user(self):
        viewer = ViewerUserFactory()
        self.client.force_authenticate(viewer)

        response = self.client.post(self.list_url, {
            "username": "newbie2",
            "email": "newbie2@example.com",
            "password": "supersecret123",
            "role": Role.EDITOR,
        })

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_assign_role(self):
        admin = AdminUserFactory()
        viewer = ViewerUserFactory()
        self.client.force_authenticate(admin)
        url = reverse("user-role-update", args=[viewer.id])

        response = self.client.patch(url, {"role": Role.EDITOR})

        assert response.status_code == status.HTTP_200_OK
        viewer.refresh_from_db()
        assert viewer.role == Role.EDITOR

    def test_me_endpoint_returns_current_user(self):
        viewer = ViewerUserFactory()
        self.client.force_authenticate(viewer)

        response = self.client.get(reverse("user-me"))

        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == viewer.username

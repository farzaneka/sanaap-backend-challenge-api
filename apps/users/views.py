from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.permissions import IsAdmin
from apps.users.serializers import (
    UserCreateSerializer,
    UserRoleUpdateSerializer,
    UserSerializer,
)

User = get_user_model()


class UserListCreateView(generics.ListCreateAPIView):
    """List all users or create a new one.

    - GET: any authenticated user can list users (read only, no sensitive
      fields exposed).
    - POST: only admins can create new users (per RBAC spec: "admin: ...
      ایجاد کاربر").
    """

    queryset = User.objects.all().order_by("id")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated(), IsAdmin()]
        return [permissions.IsAuthenticated()]


class UserRoleUpdateView(generics.UpdateAPIView):
    """Assign/change a user's role. Admins only."""

    queryset = User.objects.all()
    serializer_class = UserRoleUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    http_method_names = ["patch"]


class MeView(APIView):
    """Return the currently authenticated user's profile."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

from django.urls import path

from apps.users.views import MeView, UserListCreateView, UserRoleUpdateView

urlpatterns = [
    path("", UserListCreateView.as_view(), name="user-list-create"),
    path("me/", MeView.as_view(), name="user-me"),
    path("<int:pk>/role/", UserRoleUpdateView.as_view(), name="user-role-update"),
]

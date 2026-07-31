import factory
from django.contrib.auth import get_user_model

from apps.documents.models import Document
from apps.users.models import Role

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("username",)

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    role = Role.VIEWER

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        self.set_password(extracted or "testpass123!")
        if create:
            self.save()


class AdminUserFactory(UserFactory):
    role = Role.ADMIN
    is_staff = True


class EditorUserFactory(UserFactory):
    role = Role.EDITOR


class ViewerUserFactory(UserFactory):
    role = Role.VIEWER


class DocumentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Document

    title = factory.Sequence(lambda n: f"Document {n}")
    description = "A test document"
    owner = factory.SubFactory(UserFactory)
    content_type = "text/plain"
    size = 100
    checksum = "deadbeef"

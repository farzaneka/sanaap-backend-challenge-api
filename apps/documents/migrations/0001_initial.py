import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import apps.documents.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Document",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True, default="")),
                ("file", models.FileField(upload_to=apps.documents.models.document_upload_path, validators=[apps.documents.models.validate_file_size, apps.documents.models.validate_content_type])),
                ("content_type", models.CharField(blank=True, max_length=150)),
                ("size", models.PositiveBigIntegerField(default=0, help_text="File size in bytes.")),
                ("checksum", models.CharField(blank=True, help_text="SHA-256 hash of the file content.", max_length=64)),
                ("tags", models.CharField(blank=True, default="", help_text="Comma separated tags, used for filtering.", max_length=255)),
                ("is_processed", models.BooleanField(default=False, help_text="Set to True once the background processing task has finished.")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="documents", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "db_table": "documents",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="document",
            index=models.Index(fields=["owner", "-created_at"], name="documents_owner_i_9c1b3a_idx"),
        ),
        migrations.AddIndex(
            model_name="document",
            index=models.Index(fields=["content_type"], name="documents_content_9f2d41_idx"),
        ),
    ]

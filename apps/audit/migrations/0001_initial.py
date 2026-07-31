import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AuditLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("action", models.CharField(choices=[("view", "View"), ("create", "Create"), ("update", "Update"), ("delete", "Delete"), ("login", "Login"), ("request", "Request")], max_length=20)),
                ("resource", models.CharField(help_text="e.g. 'Document', or the request path.", max_length=100)),
                ("resource_id", models.CharField(blank=True, default="", max_length=100)),
                ("method", models.CharField(blank=True, default="", max_length=10)),
                ("path", models.CharField(blank=True, default="", max_length=500)),
                ("status_code", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="audit_logs", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "db_table": "audit_logs",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="auditlog",
            index=models.Index(fields=["user", "-created_at"], name="audit_logs_user_id_7a1e2b_idx"),
        ),
        migrations.AddIndex(
            model_name="auditlog",
            index=models.Index(fields=["resource", "resource_id"], name="audit_logs_resourc_4d6f9c_idx"),
        ),
    ]

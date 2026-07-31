import shutil
import tempfile

import pytest
from django.test import override_settings

_TEST_MEDIA_ROOT = tempfile.mkdtemp(prefix="dms-test-media-")


@pytest.fixture(autouse=True)
def use_local_storage_for_tests(settings):
    """Documents are stored via a MinIO/S3 backend in real deployments,
    but unit tests should not require a live MinIO instance. We swap in
    Django's local filesystem storage for the duration of each test.
    """
    settings.STORAGES = {
        **settings.STORAGES,
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    }
    settings.MEDIA_ROOT = _TEST_MEDIA_ROOT
    settings.CELERY_TASK_ALWAYS_EAGER = True
    yield


def pytest_sessionfinish(session, exitstatus):
    shutil.rmtree(_TEST_MEDIA_ROOT, ignore_errors=True)

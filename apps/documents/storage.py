"""
Custom storage backend pointing django-storages' S3Boto3Storage at a MinIO
instance. MinIO speaks the S3 API, so django-storages works out of the box
once endpoint_url/access keys are supplied (done via settings.py).

Keeping this as its own class (rather than configuring S3Boto3Storage
directly everywhere) gives us a single place to override behaviour later
(e.g. per-bucket policies, custom key naming) without touching settings
or the models that use it -- Open/Closed principle.
"""

from storages.backends.s3boto3 import S3Boto3Storage


class MinioMediaStorage(S3Boto3Storage):
    """Stores uploaded documents in a MinIO bucket and generates secure,
    time-limited (presigned) URLs when files are served, since
    AWS_QUERYSTRING_AUTH is enabled in settings.
    """

    location = "documents"
    file_overwrite = False
    default_acl = None

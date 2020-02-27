from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class StaticStorage(S3Boto3Storage):
    location = f"{settings.AWS_LOCATION}/{settings.STATICFILES_LOCATION}"
    default_acl = 'public-read'


class PublicMediaStorage(S3Boto3Storage):
    location = f"{settings.AWS_LOCATION}/{settings.MEDIAFILES_LOCATION}"
    default_acl = 'public-read'
    file_overwrite = False

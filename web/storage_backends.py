from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class StaticStorage(S3Boto3Storage):
    location = settings.STATIC_LOCATION
    AWS_S3_CUSTOM_DOMAIN = settings.BASE_S3_DOMAIN
    default_acl = 'public-read'


class PublicMediaStorage(S3Boto3Storage):
    location = settings.PUBLIC_MEDIA_LOCATION
    AWS_S3_CUSTOM_DOMAIN = settings.BASE_S3_DOMAIN
    default_acl = 'public-read'
    file_overwrite = False

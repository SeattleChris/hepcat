from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class StaticStorage(S3Boto3Storage):
    location = f"{settings.AWS_LOCATION}/{settings.STATICFILES_LOCATION}"
    # STATIC_URL = f'https://{settings.BASE_S3_DOMAIN}/{settings.AWS_LOCATION}/{location}/'
    # AWS_S3_CUSTOM_DOMAIN = settings.BASE_S3_DOMAIN
    default_acl = 'public-read'


class PublicMediaStorage(S3Boto3Storage):
    # location = settings.MEDIAFILES_LOCATION
    # AWS_S3_CUSTOM_DOMAIN = settings.BASE_S3_DOMAIN
    default_acl = 'public-read'
    file_overwrite = False

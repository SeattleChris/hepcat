from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings
base_s3_domain = settings.BASE_S3_DOMAIN


class StaticStorage(S3Boto3Storage):
    location = settings.STATIC_LOCATION
    STATIC_URL = f'https://{base_s3_domain}/{location}/'
    default_acl = 'public-read'


class PublicMediaStorage(S3Boto3Storage):
    location = settings.PUBLIC_MEDIA_LOCATION
    MEDIA_URL = f'https://{base_s3_domain}/{location}/'
    default_acl = 'public-read'
    file_overwrite = False

from django.test import TestCase, Client, override_settings  # , modify_settings
from unittest import skip
from django.conf import settings
from os import environ
# from django.apps import apps
# from django.conf import settings
# from os import environ
# from django.contrib.admin.sites import AdminSite
# from django.contrib.admin.models import LogEntry
# from django.contrib.auth.models import Permission
# from django.contrib.sessions.models import Session as Session_contrib
# from django.contrib.contenttypes.models import ContentType
# # from django.forms import ValidationError
# # from django.contrib import admin as default_admin
# from classwork.admin import AdminSessionForm, SessiontAdmin, admin as main_admin
# from classwork.models import Session  # , Subject, ClassOffer, Location, Profile, Registration, Payment
# from users.models import UserHC as User
# # from datetime import date, timedelta


class RouteTests(TestCase):
    """ Routes to be checked. """

    @classmethod
    def setUpClass(cls):
        c = Client()
        cls.my_client = c
        return super().setUpClass()

    def test_visit_homepage(self):
        c = Client()
        homepage = c.get('/')
        self.assertEqual(homepage.status_code, 200)

    @skip("Not Implemented")
    @override_settings(DEBUG=True)
    def test_static_on_debug(self):
        homepage = self.my_client.get('/')
        self.assertEqual(homepage.status_code, 200)


class SettingsTests(TestCase):
    """ Checking different settings triggered by different environment situations. """

    @skip("Not Implemented")
    @override_settings(HOSTED_PYTHONANYWHERE=True, LOCAL=False)
    def test_hosted_pythonanywhere_and_not_local(self):
        DB_NAME = environ.get('LIVE_DB_NAME', environ.get('DB_NAME', 'postgres'))
        USER = environ.get('LIVE_DB_USER', environ.get('DB_USER', 'postgres'))
        LOGNAME = environ.get('LOGNAME', USER)
        expected_db_name = LOGNAME + '$' + DB_NAME
        database_name = settings.DATABASES.get('default', {}).get('NAME', '')
        expected_test_name = LOGNAME + '$test_' + DB_NAME
        database_test_name = settings.DATABASES.get('TEST', {}).get('NAME', '')

        self.assertEqual(expected_db_name, database_name)
        self.assertEqual(expected_test_name, database_test_name)
        with self.assertRaises(KeyError):
            settings.DATABASES['default']['TEST']

    @skip("Not Implemented")
    @override_settings(USE_S3=True)
    def test_aws_settings(self):
        AWS_ACCESS_KEY_ID = environ.get('AWS_ACCESS_KEY_ID', '')
        AWS_SECRET_ACCESS_KEY = environ.get('AWS_SECRET_ACCESS_KEY', '')
        AWS_STORAGE_BUCKET_NAME = environ.get('AWS_STORAGE_BUCKET_NAME', '')
        AWS_S3_REGION_NAME = environ.get('AWS_S3_REGION_NAME', '')
        AWS_DEFAULT_ACL = None
        AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
        # AWS_LOCATION = 'www'
        # STATICFILES_LOCATION = 'static'
        STATICFILES_STORAGE = 'web.storage_backends.StaticStorage'
        # MEDIAFILES_LOCATION = 'media'

        self.assertEqual(AWS_ACCESS_KEY_ID, settings.AWS_ACCESS_KEY_ID)
        self.assertEqual(AWS_SECRET_ACCESS_KEY, settings.AWS_SECRET_ACCESS_KEY)
        self.assertEqual(AWS_STORAGE_BUCKET_NAME, settings.AWS_STORAGE_BUCKET_NAME)
        self.assertEqual(AWS_S3_REGION_NAME, settings.AWS_S3_REGION_NAME)
        self.assertEqual(AWS_DEFAULT_ACL, settings.AWS_DEFAULT_ACL)
        self.assertEqual(AWS_S3_OBJECT_PARAMETERS, settings.AWS_S3_OBJECT_PARAMETERS)
        self.assertEqual(STATICFILES_STORAGE, settings.STATICFILES_STORAGE)

    @skip("Not Implemented")
    def test_email_backend_else_condition(self):
        pass

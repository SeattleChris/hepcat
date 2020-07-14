from django.test import TestCase, Client, override_settings  # , modify_settings
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

    @override_settings(DEBUG=True)
    def test_static_on_debug(self):
        homepage = self.my_client.get('/')
        self.assertEqual(homepage.status_code, 200)
        # self.assertTrue(False)


class SettingsFileTests(TestCase):
    """ Coverage reports some sections of settings file that need testing. """

    def test_hosted_pythonanywhere_and_not_local(self):
        pass

    def test_use_s3(self):
        pass

    def test_email_backend_else_condition(self):
        pass

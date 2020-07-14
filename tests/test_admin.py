from django.test import TestCase, Client
from django.apps import apps
from django.conf import settings
from os import environ
from django.contrib.admin.sites import AdminSite
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Permission
from django.contrib.sessions.models import Session as Session_contrib
from django.contrib.contenttypes.models import ContentType
# from django.forms import ValidationError
# from django.contrib import admin as default_admin
from classwork.admin import AdminSessionForm, SessiontAdmin, admin as main_admin
from classwork.models import Session  # , Subject, ClassOffer, Location, Profile, Registration, Payment
from users.models import UserHC as User
from datetime import date, timedelta
# from django.contrib.auth import get_user_model
# User = get_user_model()


class AdminSetupTests(TestCase):
    """ General expectations of the Admin. """

    def test_admin_set_for_all_models(self):
        """ Make sure all models can be managed in the admin. """
        models = apps.get_models()
        registered_admins_dict = main_admin.site._registry
        registered_models = list(registered_admins_dict.keys())
        models.remove(LogEntry)
        models.remove(Permission)
        models.remove(ContentType)
        models.remove(Session_contrib)
        for model in models:
            self.assertIn(model, registered_models)

    def test_createsu_command(self):
        """ Our custom command to create a Superuser as an initial admin """
        # TODO: Write tests for when there is no superuser.
        # This seemed to not work when using this command on PythonAnywhere the first time
        pass


class AdminSessionModelManagement(TestCase):
    """ Tests for Session model create or modify in the Admin site. """

    def test_admin_uses_correct_admin(self):
        """ The admin site should use the SessiontAdmin for the Session model. """
        registered_admins_dict = main_admin.site._registry
        sess_admin = registered_admins_dict.get(Session, None)
        self.assertIsInstance(sess_admin, SessiontAdmin)

    def test_admin_uses_expected_form(self):
        """ The admin SessiontAdmin utilizes the correct AdminSessionForm. """
        current_admin = SessiontAdmin(model=Session, admin_site=AdminSite())
        form = getattr(current_admin, 'form', None)
        form_class = AdminSessionForm
        self.assertEquals(form, form_class)

    def test_admin_has_all_model_fields(self):
        """ The admin SessiontAdmin should use all the fields of the Session model. """
        current_admin = SessiontAdmin(model=Session, admin_site=AdminSite())
        admin_fields = []
        if current_admin.fields:
            for ea in current_admin.fields:
                if not isinstance(ea, (list, tuple)):
                    ea = [ea]
                admin_fields.extend(ea)
        if current_admin.fieldsets:
            for ea in current_admin.fieldsets:
                admin_fields.extend(ea[1].get('fields', []))
        model_fields = [field.name for field in Session._meta.get_fields(include_parents=False)]
        model_fields.remove('id')
        model_fields.remove('date_added')
        model_fields.remove('date_modified')
        model_fields.remove('classoffer')
        admin_fields = tuple(admin_fields)
        model_fields = tuple(model_fields)
        self.assertTupleEqual(admin_fields, model_fields)

    def get_login_kwargs(self):
        """ If we need an admin login, this will be the needed dictionary to pass as kwargs. """
        password = environ.get('SUPERUSER_PASS', '')
        admin_user_email = environ.get('SUPERUSER_EMAIL', settings.ADMINS[0][1])
        # user = User.objects.create_user(email=admin_user_email, is_admin=True)
        user = User.objects.create_superuser(admin_user_email, admin_user_email, password)
        # user.set_password(password)
        # user.save()
        print('----------------- Made User ----------------------')
        print(user.username)
        return {'username': admin_user_email, 'password': password}

    def response_after_login(self, url, client):
        """ If the url requires a login, perform a login and follow the redirect. """
        get_response = client.get(url)
        if 'url' in get_response:
            login_kwargs = self.get_login_kwargs()
            login_attempt = client.post(get_response.url, login_kwargs)
            print('===========================================')
            print(login_attempt)
            get_response = client.get(url)
        return get_response

    def test_admin_can_create_first_session(self):
        """ The first Session can be made, even though later Sessions get defaults from existing ones. """
        # from pprint import pprint
        c = Client()
        add_url = '/admin/classwork/session/add/'
        login_kwargs = self.get_login_kwargs()
        login_try = c.login(**login_kwargs)
        # print('==================================================================')
        # pprint(login_try)
        # get_add_template = c.get(add_url)
        # get_add_template = self.response_after_login(add_url, c)
        # print('==================================================================')
        # pprint(get_add_template)
        # print('==================================================================')
        key_day, name = date.today(), 'test_create'
        kwargs = {'key_day_date': key_day, 'name': name}
        kwargs['max_day_shift'] = 2
        kwargs['num_weeks'] = 5
        kwargs['skip_weeks'] = 0
        kwargs['break_weeks'] = 0
        kwargs['publish_date'] = key_day - timedelta(days=7*3+1)
        kwargs['expire_date'] = key_day + timedelta(days=7+1)
        post_response = c.post(add_url, kwargs, follow=True)
        # pprint(post_response)
        # print('==================================================================')
        # if 'url' in post_response:
        #     redirect_response = c.get(post_response.url)
        #     pprint(redirect_response)
        sess = Session.objects.filter(name=name).first()

        self.assertTrue(login_try)
        # self.assertIsInstance(get_add_template, get_add_template)
        self.assertEquals(post_response.status_code, 200)
        self.assertIsNotNone(sess)
        self.assertIsInstance(sess, Session)

    def test_auto_correct_on_date_conflict(self):
        """ Expect a ValidationError when Sessions have overlapping dates. """
        key_day, name = date.today(), 'first'
        publish = key_day - timedelta(days=7*3+1)
        first_sess = Session.objects.create(name=name, key_day_date=key_day, num_weeks=5, publish_date=publish)
        sess = Session.objects.filter(name=name).first()
        self.assertIsNotNone(sess)
        self.assertIsInstance(sess, Session)
        self.assertEquals(first_sess, sess)

        c = Client()
        add_url = '/admin/classwork/session/add/'
        login_kwargs = self.get_login_kwargs()
        login_try = c.login(**login_kwargs)
        key_day += timedelta(days=7)
        kwargs = {'key_day_date': key_day, 'name': 'test_create'}
        kwargs['max_day_shift'] = 2
        kwargs['num_weeks'] = 5
        kwargs['skip_weeks'] = 0
        kwargs['break_weeks'] = 0
        kwargs['publish_date'] = key_day - timedelta(days=7*3+1)
        kwargs['expire_date'] = key_day + timedelta(days=7+1)

        self.assertTrue(login_try)
        # with self.assertRaises(ValidationError):
        post_response = c.post(add_url, kwargs, follow=True)
        template_target = 'admin/classwork/session/change_form.html'
        self.assertIn(template_target, post_response.template_name)
        print(post_response.template_name)
        self.assertEquals(post_response.status_code, 200)
        second_sess = Session.objects.filter(name=name).first()
        # pprint(second_sess)
        self.assertGreater(first_sess.end_date, second_sess.start_date)

    def test_auto_correct_on_flip_but_no_skip(self):
        # TODO: write test for when flip_last_day is True, but skip_weeks == 0.
        pass

from django.test import TestCase, Client
from unittest import skip
from django.apps import apps
from django.conf import settings
from os import environ
from django.contrib.admin.sites import AdminSite
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Permission
from django.contrib.auth.forms import UserChangeForm  # , UserCreationForm
from django.contrib.sessions.models import Session as Session_contrib
from django.contrib.contenttypes.models import ContentType
# from django.forms import ValidationError
from classwork.admin import AdminSessionForm, ClassOfferAdmin, SessiontAdmin, ClassDayListFilter, RegistrationAdmin
from classwork.admin import admin as main_admin
from classwork.models import Session, ClassOffer, Subject  # , Location, Profile, Registration, Payment
from users.admin import CustomUserAdmin
from users.models import UserHC as User
from datetime import date, time, timedelta
from copy import deepcopy
from types import GeneratorType
from pprint import pprint


class MockRequest:
    pass


class MockSuperUser:
    def has_perm(self, perm):
        return True


request = MockRequest()
request.user = MockSuperUser()


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

    @skip("Not Implemented")
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
        User.objects.create_superuser(admin_user_email, admin_user_email, password)
        return {'username': admin_user_email, 'password': password}

    def response_after_login(self, url, client):
        """ If the url requires a login, perform a login and follow the redirect. """
        get_response = client.get(url)
        if 'url' in get_response:
            login_kwargs = self.get_login_kwargs()
            client.post(get_response.url, login_kwargs)
            get_response = client.get(url)
        return get_response

    def test_admin_can_create_first_session(self):
        """ The first Session can be made, even though later Sessions get defaults from existing ones. """
        c = Client()
        add_url = '/admin/classwork/session/add/'
        login_kwargs = self.get_login_kwargs()
        login_try = c.login(**login_kwargs)
        key_day, name = date.today(), 'test_create'
        kwargs = {'key_day_date': key_day, 'name': name}
        kwargs['max_day_shift'] = 2
        kwargs['num_weeks'] = 5
        kwargs['skip_weeks'] = 0
        kwargs['break_weeks'] = 0
        kwargs['publish_date'] = key_day - timedelta(days=7*3+1)
        kwargs['expire_date'] = key_day + timedelta(days=7+1)
        post_response = c.post(add_url, kwargs, follow=True)
        sess = Session.objects.filter(name=name).first()

        self.assertTrue(login_try)
        self.assertEquals(post_response.status_code, 200)
        self.assertIsNotNone(sess)
        self.assertIsInstance(sess, Session)

    def test_auto_correct_on_date_conflict(self):
        """ Expect a ValidationError when Sessions have overlapping dates. """
        key_day, name = date.today(), 'first'
        publish = key_day - timedelta(days=7*3+1)
        first_sess = Session.objects.create(name=name, key_day_date=key_day, num_weeks=5, publish_date=publish)
        sess = Session.objects.filter(name=name).first()

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
        post_response = c.post(add_url, kwargs, follow=True)
        template_target = 'admin/classwork/session/change_form.html'
        second_sess = Session.objects.filter(name=name).first()

        self.assertIsNotNone(sess)
        self.assertIsInstance(sess, Session)
        self.assertEquals(first_sess, sess)
        self.assertTrue(login_try)
        self.assertIn(template_target, post_response.template_name)
        self.assertEquals(post_response.status_code, 200)
        self.assertGreater(first_sess.end_date, second_sess.start_date)

    def test_form_clean_validation_error_message(self):
        key_day, name = date.today(), 'first'
        publish = key_day - timedelta(days=7*3+1)
        sess = Session.objects.create(name=name, key_day_date=key_day, num_weeks=5, publish_date=publish)

        c = Client()
        add_url = '/admin/classwork/session/add/'
        login_kwargs = self.get_login_kwargs()
        login_try = c.login(**login_kwargs)
        key_day += timedelta(days=7)
        kwargs = {'key_day_date': key_day, 'name': 'test_create'}
        kwargs['max_day_shift'] = -2
        kwargs['skip_weeks'] = 0
        kwargs['flip_last_day'] = True
        post_response = c.post(add_url, kwargs)
        errors = post_response.context_data.get('errors', [[]])
        string = "Overlapping class dates with those settings. "
        string += "You could move the other class days to happen after the main day, "
        # string += "You could "
        string += "add a break week on the previous session, or otherwise change when this session starts. "

        self.assertTrue(login_try)
        self.assertIsNotNone(sess)
        self.assertIsInstance(sess, Session)
        self.assertEqual(string, errors[-1][0])
        # with self.assertRaises(ValidationError):
        #     c.post(add_url, kwargs)

    @skip("Not Implemented")
    def test_auto_correct_on_flip_but_no_skip(self):
        # TODO: write test for when flip_last_day is True, but skip_weeks == 0.
        pass


class AdminClassOfferTests(TestCase):

    def test_admin_uses_correct_admin(self):
        registered_admins_dict = main_admin.site._registry
        sess_admin = registered_admins_dict.get(ClassOffer, None)
        self.assertIsInstance(sess_admin, ClassOfferAdmin)

    def test_time_column(self):
        key_day, name = date.today(), 'first'
        publish = key_day - timedelta(days=7*3+1)
        sess1 = Session.objects.create(name=name, key_day_date=key_day, num_weeks=5, publish_date=publish)
        sess2 = Session.objects.create(name='second')
        subj = Subject.objects.create(version=Subject.VERSION_CHOICES[0][0], num_minutes=60, title="test_subj")
        subj2 = Subject.objects.create(version=Subject.VERSION_CHOICES[0][0], num_minutes=90, title="subj2")
        first = ClassOffer.objects.create(subject=subj, session=sess1, start_time=time(19, 0))
        second = ClassOffer.objects.create(subject=subj, session=sess2, start_time=time(19, 30))
        third = ClassOffer.objects.create(subject=subj2, session=sess2, start_time=time(19, 0))
        current_admin = ClassOfferAdmin(model=ClassOffer, admin_site=AdminSite())

        time_1 = current_admin.time(first)
        time_2 = current_admin.time(second)
        time_3 = current_admin.time(third)
        expected_time_1 = '7pm - 8pm'
        expected_time_2 = '7:30pm - 8:30pm'
        expected_time_3 = '7:00pm - 8:30pm'

        self.assertEqual(expected_time_1, time_1)
        self.assertEqual(expected_time_2, time_2)
        self.assertEqual(expected_time_3, time_3)

    def test_time_not_set(self):
        key_day, name = date.today(), 'first'
        publish = key_day - timedelta(days=7*3+1)
        sess1 = Session.objects.create(name=name, key_day_date=key_day, num_weeks=5, publish_date=publish)
        subj = Subject.objects.create(version=Subject.VERSION_CHOICES[0][0], num_minutes=0, title="test_subj")
        first = ClassOffer.objects.create(subject=subj, session=sess1, start_time=time(19, 0))
        current_admin = ClassOfferAdmin(model=ClassOffer, admin_site=AdminSite())

        time_1 = current_admin.time(first)
        expected_time = 'Not Set'
        self.assertEqual(expected_time, time_1)


class AdminClassDayListFilterTests(TestCase):
    # related_models = (ClassOfferAdmin, RegistrationAdmin)

    def test_admin_classoffer_lookup(self):
        key_day, name = date.today(), 'sess1'
        publish = key_day - timedelta(days=7*3+1)
        sess1 = Session.objects.create(name=name, key_day_date=key_day, max_day_shift=6, publish_date=publish)
        subj = Subject.objects.create(version=Subject.VERSION_CHOICES[0][0], title="test_subj")
        kwargs = {'subject': subj, 'session': sess1, 'start_time': time(19, 0)}
        classoffers = [ClassOffer.objects.create(class_day=k, **kwargs) for k, v in ClassOffer.DOW_CHOICES if k % 2]
        expected_lookup_list = [(k, v) for k, v in ClassOffer.DOW_CHOICES if k % 2]

        current_admin = ClassOfferAdmin(model=ClassOffer, admin_site=AdminSite())
        day_filter = ClassDayListFilter(request, {}, ClassOffer, current_admin)
        lookup = day_filter.lookups(request, current_admin)

        self.assertEqual(len(classoffers), 3)
        self.assertEqual(ClassOffer.objects.count(), 3)
        self.assertEqual(len(lookup), 3)
        self.assertIsInstance(lookup, GeneratorType)
        self.assertEquals(expected_lookup_list, list(lookup))
        # qs = current_admin.get_queryset(request)
        # query = day_filter.queryset(request, qs)

    # end AdminClassDayListFilterTests


class AdminUserHCTests(TestCase):

    def test_admin_uses_correct_admin(self):
        """ The admin site should use the CustomUserAdmin for the UserHC model. """
        registered_admins_dict = main_admin.site._registry
        user_admin = registered_admins_dict.get(User, None)
        self.assertIsInstance(user_admin, CustomUserAdmin)

    def test_admin_uses_expected_form(self):
        """ The admin CustomUserAdmin utilizes the correct form. """
        current_admin = CustomUserAdmin(model=User, admin_site=AdminSite())
        form = getattr(current_admin, 'form', None)
        form_class = UserChangeForm
        self.assertEquals(form, form_class)
        # self.assertIsInstance(form, form_class)

    def test_get_form_uses_custom_formfield_attrs_overrides(self):
        current_admin = CustomUserAdmin(model=User, admin_site=AdminSite())
        form = current_admin.get_form(request)
        fields = form.base_fields
        expected_values = deepcopy(current_admin.formfield_attrs_overrides)
        expected_values = {key: value for key, value in expected_values.items() if key in fields}
        actual_values = {}
        for name, field_attrs in expected_values.items():
            if 'size' in field_attrs and 'no_size_override' not in field_attrs:
                input_size = float(fields[name].widget.attrs.get('maxlength', float("inf")))
                field_attrs['size'] = str(int(min(int(field_attrs['size']), input_size)))  # Modify expected_values
            actual_values[name] = {key: fields[name].widget.attrs.get(key) for key in field_attrs}

        self.assertDictEqual(expected_values, actual_values)

    def test_get_form_modifies_input_size_for_small_maxlength_fields(self):
        current_admin = CustomUserAdmin(model=User, admin_site=AdminSite())
        form = current_admin.get_form(request)
        expected_values, actual_values = {}, {}
        for name, field in form.base_fields.items():
            if not current_admin.formfield_attrs_overrides.get(name, {}).get('no_size_override', False):
                display_size = float(field.widget.attrs.get('size', float('inf')))
                input_size = int(field.widget.attrs.get('maxlength', 0))
                if input_size:
                    expected_values[name] = str(int(min(display_size, input_size)))
                    actual_values[name] = field.widget.attrs.get('size', '')

        self.assertDictEqual(expected_values, actual_values)

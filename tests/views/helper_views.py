from django.test import Client, RequestFactory  # , TestCase,  TransactionTestCase
from django.urls import reverse
# from unittest import skip  # @skip("Not Implemented")
from django.conf import settings
from django.utils.module_loading import import_string
from datetime import time, timedelta, datetime as dt  # date,
decide_session = import_string('classwork.views.decide_session')
Staff = import_string('classwork.models.Staff')
Student = import_string('classwork.models.Student')
SiteContent = import_string('classwork.models.SiteContent')
Session = import_string('classwork.models.Session')
Subject = import_string('classwork.models.Subject')
ClassOffer = import_string('classwork.models.ClassOffer')
# , Location, Resource, SiteContent, Profile, Payment, Registration, Notify
UserHC = import_string('users.models.UserHC')
AnonymousUser = import_string('django.contrib.auth.models.AnonymousUser')
USER_DEFAULTS = {'email': 'user_fake@fakesite.com', 'password': '1234', 'first_name': 'f_user', 'last_name': 'fake_y'}
OTHER_USER = {'email': 'other@fakesite.com', 'password': '1234', 'first_name': 'other_user', 'last_name': 'fake_y'}


class TestFormLoginRequired:
    url_name = ''  # 'url_name' for the desired path '/url/to/view'
    # url = reverse(url_name)
    login_cred = {'username': '', 'password': ''}    # defined in fixture or with factory in setUp()
    viewClass = None
    expected_template = getattr(viewClass, 'template_name', '')
    expected_form = ''
    expected_error_field = ''
    login_redirect = '/login/'
    success_redirect = ''
    bad_data = {}
    good_data = {}

    def test_call_view_deny_anonymous(self):
        """ Login is required for either get or post. """
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.login_redirect)
        response = self.client.post(self.url, follow=True)
        self.assertRedirects(response, self.login_redirect)

    def test_call_view_load(self):
        """ After login, can get the form. """
        self.client.login(**self.login_cred)
        response = self.client.get(self.url)
        # self.assertContains()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.expected_template)

    def test_call_view_fail_blank(self):
        """ Submitting a blank form should get a form error. """
        self.client.login(**self.login_cred)
        data = {}  # blank data dictionary (on purpose)
        response = self.client.post(self.url, data)
        self.assertFormError(response, self.expected_form, self.expected_error_field, 'This field is required.')
        # etc. ...

    def test_call_view_fail_invalid(self):
        """ Submitting an invalid form should get a form error. """
        self.client.login(**self.login_cred)
        response = self.client.post(self.url, self.bad_data)
        self.assertFormError(response, self.expected_form, self.expected_error_field, 'This field is required.')

    def test_call_view_success_invalid(self):
        """ Submitting a valid form should give expected redirect. """
        self.client.login(**self.login_cred)
        response = self.client.post(self.url, self.bad_data)
        self.assertRedirects(response, self.success_redirect)


class MimicAsView:
    url_name = ''  # find in app.urls
    viewClass = None  # find in app.views
    query_order_by = None  # expected tuple or list if order_by is needed.

    def setup_view(self, method, req_kwargs=None, template_name=None, *args, **init_kwargs):
        """A view instance that mimics as_view() returned callable. For args and kwargs match format as reverse(). """
        req_kwargs = req_kwargs or {}
        if isinstance(method, str):
            method = method.lower()
        allowed_methods = getattr(self.viewClass, 'http_method_names', {'get', })
        if method not in allowed_methods or not getattr(self.viewClass, method, None):
            raise ValueError("Method '{}' not recognized as an allowed method string. ".format(method))
        factory = RequestFactory()
        request = getattr(factory, method)('/', **req_kwargs)

        key = 'template_name'
        template_name = template_name or getattr(self, key, None) or getattr(self.viewClass, key, None)
        view = self.viewClass(template_name=template_name, **init_kwargs)
        # emulate View.setup()
        view.request = request
        view.args = args
        view.kwargs = init_kwargs
        return view

    def prep_http_method(self, method):
        # # emulate View.as_view() would seem to put these on EACH http method of view.
        method.view_class = self.viewClass
        method.init_kwargs = self.kwargs
        return method

    def setup_three_sessions(self):
        levels = [lvl for lvl, display in Subject.LEVEL_CHOICES]
        ver = Subject.VERSION_CHOICES[0][0]
        subjs = [Subject.objects.create(level=lvl, version=ver, title='_'.join((lvl, ver))) for lvl in levels]
        dur = settings.DEFAULT_SESSION_WEEKS
        now = dt.utcnow().date()
        class_day = now.weekday()
        sess_names = ['old_sess', 'curr_sess', 'new_sess']
        classoffers = {}
        for num, name in enumerate(sess_names):
            key_date = now + timedelta(days=7*dur*(num - 1))
            sess = Session.objects.create(name=name, key_day_date=key_date)
            co_kwargs = {'session': sess, 'start_time': time(19, 0), 'class_day': class_day}
            classoffers[name] = [ClassOffer.objects.create(subject=subj, **co_kwargs) for subj in subjs]
        return classoffers

    def client_visit_view(self, good_text, bad_text=None, url_name=None):
        url_name = url_name or self.url_name
        if not isinstance(url_name, str):
            raise TypeError("Need a string for the url_name. ")
        if not isinstance(good_text, str):
            raise TypeError("Must have a string for 'good_text' parameter. ")
        if bad_text is not None and not isinstance(bad_text, str):
            raise TypeError("If included, must have a string for 'bad_text' parameter. ")
        url = reverse(url_name)
        c = Client()
        response = c.get(url)
        self.assertEqual(response.status_code, 200)
        if bad_text:
            self.assertNotContains(response, bad_text)
        self.assertContains(response, good_text)

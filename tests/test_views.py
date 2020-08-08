from django.test import Client, TestCase  # , TransactionTestCase
from django.urls import reverse
from unittest import skip
from django.conf import settings
# from .helper import SimpleModelTests
from classwork.views import decide_session, AboutUsListView, ClassOfferListView
# , SubjectProgressView, ClassOfferDetailView, Checkin
from classwork.models import Staff, Student, SiteContent
from classwork.models import Session, Subject, ClassOffer  # , Location, Resource, SiteContent, Profile
# from classwork.models import Payment, Registration, Notify
from users.models import UserHC
from datetime import date, time, timedelta, datetime as dt
# @skip("Not Implemented")
USER_DEFAULTS = {'email': 'user_fake@fakesite.com', 'password': '1234', 'first_name': 'f_user', 'last_name': 'fake_y'}


class AboutUsListTests(TestCase):
    ProfileStaff_query = Staff.objects  # Profile.objects.filter(is_staff=True) if single Profile model.
    ProfileStudent_query = Student.objects  # Profile.objects.filter(is_student=True) if single Profile model.

    def get_staff_list(self, transform, is_ordered):
        """ Used to get the transformed list of expected staff users. """
        staff_query = self.ProfileStaff_query.filter(user__is_active=True)
        if is_ordered:
            order = getattr(self, 'query_order_by', [])
            staff_query = staff_query.order_by(*order) if order else staff_query
        return [transform(ea) for ea in staff_query.all()]

    def test_queryset_has_active_admin(self):
        """ The queryset should have currently active admin staff members. """
        kwargs = USER_DEFAULTS.copy()
        kwargs['is_admin'] = True
        user = UserHC.objects.create_user(**kwargs)
        user.save()
        staff = getattr(user, 'staff', None)
        view = AboutUsListView()
        view_queryset = view.get_queryset()
        is_ordered = getattr(view_queryset, 'ordered', False)
        transform = repr
        all_staff_list = self.get_staff_list(transform, is_ordered)

        self.assertTrue(user.is_staff)
        self.assertQuerysetEqual(view_queryset, all_staff_list, transform=transform, ordered=is_ordered)
        self.assertIsNotNone(staff)
        self.assertIn(staff, list(view_queryset.all()))

    def test_queryset_has_active_teachers(self):
        """ The queryset should have currently active teacher staff members. """
        kwargs = USER_DEFAULTS.copy()
        kwargs['is_teacher'] = True
        user = UserHC.objects.create_user(**kwargs)
        user.save()
        staff = getattr(user, 'staff', None)
        view = AboutUsListView()
        view_queryset = view.get_queryset()
        is_ordered = getattr(view_queryset, 'ordered', False)
        transform = repr
        all_staff_list = self.get_staff_list(transform, is_ordered)

        self.assertTrue(user.is_staff)
        self.assertQuerysetEqual(view_queryset, all_staff_list, transform=transform, ordered=is_ordered)
        self.assertIsNotNone(staff)
        self.assertIn(staff, list(view_queryset.all()))

    def test_queryset_not_have_inactive_staff(self):
        """ The queryset should not have inactive staff users. """
        kwargs = USER_DEFAULTS.copy()
        kwargs['is_teacher'] = True
        kwargs['is_active'] = False
        user = UserHC.objects.create_user(**kwargs)
        user.save()
        staff = getattr(user, 'staff', None)
        view = AboutUsListView()
        view_queryset = view.get_queryset()
        is_ordered = getattr(view_queryset, 'ordered', False)
        transform = repr
        all_staff_list = self.get_staff_list(transform, is_ordered)

        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_active)
        self.assertQuerysetEqual(view_queryset, all_staff_list, transform=transform, ordered=is_ordered)
        self.assertIsNotNone(staff)
        self.assertNotIn(staff, list(view_queryset.all()))
        self.assertIn(staff, self.ProfileStaff_query.filter(user__is_active=False))

    def test_queryset_not_have_students(self):
        """ The queryset should not have student only users. """
        kwargs = USER_DEFAULTS.copy()
        kwargs['is_admin'] = False
        kwargs['is_student'] = True
        user = UserHC.objects.create_user(**kwargs)
        user.save()
        staff = getattr(user, 'staff', None)
        student = getattr(user, 'student', None)
        view = AboutUsListView()
        view_queryset = view.get_queryset()
        is_ordered = getattr(view_queryset, 'ordered', False)
        transform = repr
        all_staff_list = self.get_staff_list(transform, is_ordered)
        users_from_view_qs = [getattr(ea, 'user', None) for ea in view_queryset.all()]
        student_query = self.ProfileStudent_query.filter(user__is_active=True)

        self.assertTrue(user.is_student)
        self.assertFalse(user.is_staff)
        self.assertQuerysetEqual(view_queryset, all_staff_list, transform=transform, ordered=is_ordered)
        self.assertIsNone(staff)
        self.assertNotIn(user, users_from_view_qs)
        self.assertIsNotNone(student)
        self.assertIn(student, list(student_query.all()))

    @skip("Not Implemented")
    def test_queryset_has_expected_profile_order(self):
        """ The queryset should have currently active staff members. """
        kwargs = USER_DEFAULTS.copy()
        kwargs['is_admin'] = True
        user = UserHC.objects.create_user(**kwargs)
        user.save()
        view = AboutUsListView()
        view_queryset = view.get_queryset()
        is_ordered = getattr(view_queryset, 'ordered', False)
        transform = repr
        all_staff_list = self.get_staff_list(transform, is_ordered)
        self.assertTrue(user.is_staff)
        self.assertQuerysetEqual(view_queryset, all_staff_list, transform=transform, ordered=is_ordered)

    def test_get_context_data(self):
        """ Testing site before and after having a 'business_about' SiteContent.  """
        target_name = 'business_about'
        test_text = 'This is the about text we added. '
        initial_about = SiteContent.objects.filter(name=target_name).first()
        initial_about = getattr(initial_about, 'text', '') if initial_about else ''
        c = Client()
        url = reverse("aboutus")
        initial_response = c.get(url)
        about = SiteContent.objects.create(name=target_name, text=test_text)
        about.save()
        later_response = c.get(url)

        self.assertEqual(initial_response.status_code, 200)
        self.assertEqual(later_response.status_code, 200)
        self.assertNotContains(initial_response, test_text)
        self.assertContains(later_response, about.text)
        self.assertEqual(test_text, about.text)


class TestFormLoginRequired:
    url_name = ''  # 'url_name' for the desired path '/url/to/view'
    # url = reverse(url_name)
    login_cred = {'username': '', 'password': ''}    # defined in fixture or with factory in setUp()
    expected_template = ''
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


class ClassOfferListViewTests(TestCase):
    url_name = 'classoffer_list'  # '/url/to/view'
    url = reverse(url_name)
    expected_template = ''
    viewClass = ClassOfferListView()
    modelClass = ClassOffer
    query_order_by = ('session__key_day_date', '_num_level', )

    def setUp(self):
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
        self.classoffers = classoffers

    # @skip("Not Implemented")
    def test_get_queryset(self):
        """ Expect to only contain the Sessions returned by decide_session as requested (or default). """
        view_queryset = self.viewClass.get_queryset()
        is_ordered = getattr(view_queryset, 'ordered', False)
        transform = repr
        sessions = decide_session()
        model_query = ClassOffer.objects.filter(session__in=sessions)
        found_query = model_query
        if is_ordered:
            order = getattr(self, 'query_order_by', [])
            model_query = model_query.order_by(*order) if order else model_query
        model_list = [transform(ea) for ea in model_query.all()]
        expected_list = [transform(ea) for ea in self.classoffers['curr_sess']]

        self.assertQuerysetEqual(view_queryset, model_list, transform=transform, ordered=is_ordered)
        self.assertQuerysetEqual(found_query, expected_list, transform=transform, ordered=False)
        self.assertQuerysetEqual(view_queryset, expected_list, transform=transform, ordered=False)

    # @skip("Not Implemented")
    def test_get_context_data(self):
        # kwargs = {}
        sessions = decide_session()
        context_sessions = ', '.join([ea.name for ea in sessions])
        expected_subset = {'sessions': context_sessions}
        display_session_subset = {'display_session': None}
        display_date_subset = {'display_date': None}
        actual = self.viewClass.get_context_data()

        self.assertDictContainsSubset(expected_subset, actual)
        self.assertDictContainsSubset(display_session_subset, actual)
        self.assertDictContainsSubset(display_date_subset, actual)


class CheckinViewTests(TestCase):

    @skip("Not Implemented")
    def test_get_queryset(self):
        pass

    @skip("Not Implemented")
    def test_get_context_data(self):
        pass


class ProfileViewTests(TestCase):

    @skip("Not Implemented")
    def test_get_object(self):
        pass

    @skip("Not Implemented")
    def test_get_context_data(self):
        pass


class RegisterViewTests(TestCase):

    @skip("Not Implemented")
    def test_get_form_kwargs(self):
        pass

    @skip("Not Implemented")
    def test_get_initial(self):
        pass

    @skip("Not Implemented")
    def test_get_success_url(self):
        pass


class PaymentProcessViewTests(TestCase):

    @skip("Not Implemented")
    def test_get_context_data(self):
        pass


class Views_payment_details_Tests(TestCase):

    @skip("Not Implemented")
    def test_raise_404_no_object(self):
        pass

    @skip("Not Implemented")
    def test_redirect_to(self):
        pass

    @skip("Not Implemented")
    def test_template_response(self):
        pass

# end test_views.py

from django.test import Client, TestCase  # , TransactionTestCase
from django.urls import reverse
from unittest import skip
# from .helper import SimpleModelTests
from classwork.views import decide_session, AboutUsListView, ClassOfferListView
# , SubjectProgressView, ClassOfferDetailView, Checkin
from classwork.models import Staff, SiteContent
from users.models import UserHC
from classwork.models import ClassOffer  # , Location, Resource, SiteContent, Subject, Profile
# from classwork.models import Session, Payment, Registration, Notify
# from datetime import date, timedelta
# @skip("Not Implemented")
USER_DEFAULTS = {'email': 'user_fake@fakesite.com', 'password': '1234', 'first_name': 'f_user', 'last_name': 'fake_y'}


class AboutUsListTests(TestCase):
    ProfileStaff_query = Staff.objects  # Profile.objects.filter(is_staff=True) if single Profile model.

    def test_queryset_is_only_active_staff(self):
        kwargs = USER_DEFAULTS.copy()
        kwargs['is_admin'] = True
        user = UserHC.objects.create_user(**kwargs)
        user.save()
        view = AboutUsListView()
        view_queryset = view.get_queryset()
        is_ordered = getattr(view_queryset, 'ordered', False)
        staff_query = self.ProfileStaff_query.filter(user__is_active=True)
        if is_ordered:
            order = getattr(self, 'query_order_by', [])
            staff_query = staff_query.order_by(*order) if order else staff_query
        transform = repr
        all_staff_list = [transform(ea) for ea in staff_query.all()]

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


class ClassOfferListViewTests(TestCase):
    view = ClassOfferListView.as_view()
    # view.kwargs = {}
    client = Client()

    # @skip("Not Implemented")
    def test_get_queryset(self):
        """ Expect to only contain the Sessions returned by decide_session as requested (or default). """
        # kwargs = {}
        sessions = decide_session()
        expected_qs = ClassOffer.objects.filter(session__in=sessions)
        expected_qs = expected_qs.order_by('session__key_day_date', '_num_level').all()
        expected = [repr(ea) for ea in expected_qs]
        actual = self.view.get_queryset()

        self.assertQuerysetEqual(actual, expected)

    # @skip("Not Implemented")
    def test_get_context_data(self):
        # kwargs = {}
        sessions = decide_session()
        context_sessions = ', '.join([ea.name for ea in sessions])
        expected_subset = {'sessions': context_sessions}
        display_session_subset = {'display_session': None}
        display_date_subset = {'display_date': None}
        actual = self.view.get_context_data()

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

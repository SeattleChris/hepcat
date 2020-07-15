from django.test import Client, TestCase  # , TransactionTestCase
from django.urls import reverse
from unittest import skip
# from .helper import SimpleModelTests
from classwork.views import AboutUsListView  # , SubjectProgressView, ClassOfferDetailView, ClassOfferListView, Checkin
from classwork.models import Profile, SiteContent
from users.models import UserHC
# from classwork.models import Location, Resource, SiteContent, Subject, ClassOffer, Profile
# from classwork.models import Session, Payment, Registration, Notify
# from datetime import date, timedelta
# @skip("Not Implemented")
USER_DEFAULTS = {'email': 'user_fake@fakesite.com', 'password': '1234', 'first_name': 'f_user', 'last_name': 'fake_y'}


class AboutUsListTests(TestCase):

    def test_queryset_is_only_staff(self):
        kwargs = USER_DEFAULTS.copy()
        kwargs['is_admin'] = True
        user = UserHC.objects.create_user(**kwargs)
        user.save()
        view = AboutUsListView()
        view_queryset = view.get_queryset()
        is_ordered = getattr(view_queryset, 'ordered', False)
        staff_query = Profile.objects.filter(user__is_staff=True)
        if is_ordered:
            order = getattr(self, 'query_order_by', [])
            staff_query = staff_query.order_by(*order) if order else staff_query
        transform = repr
        all_staff_list = [transform(ea) for ea in staff_query.all()]

        self.assertTrue(user.is_staff)
        self.assertQuerysetEqual(view_queryset, all_staff_list, transform=transform, ordered=is_ordered)

    def test_get_context_data(self):
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


class CheckinViewTests(TestCase):

    @skip("Not Implemented")
    def test_get_queryset(self):
        pass

    @skip("Not Implemented")
    def test_get_context_data(self):
        pass


class ClassOfferListViewTests(TestCase):

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

from django.test import TestCase  # , Client, RequestFactory, TransactionTestCase
from unittest import skip
from .helper_views import MimicAsView  # , UserHC, AnonymousUser, USER_DEFAULTS, OTHER_USER
# , decide_session, Staff, Student, Session, Subject, ClassOffer
from django.utils.module_loading import import_string
# , Location, Resource, SiteContent, Profile, Payment, Registration, Notify
# @skip("Not Implemented")


@skip("Not Implemented")
class RegisterCreateViewTests(MimicAsView, TestCase):
    url_name = 'register'
    viewClass = RegisterView = import_string('classwork.views.RegisterView')

    @skip("Not Implemented")
    def test_get_form_kwargs(self):
        pass

    @skip("Not Implemented")
    def test_get_initial(self):
        pass

    @skip("Not Implemented")
    def test_get_success_url(self):
        pass


@skip("Not Implemented")
class PaymentProcessViewTests(MimicAsView, TestCase):
    url_name = 'payment_success'
    viewClass = PaymentProcessView = import_string('classwork.views.PaymentProcessView')
    fail_url_name = 'payment_fail'
    fail_template_name = 'payment/fail.html'
    done_url_name = 'payment_done'
    done_template_name = 'payment/success.html'

    @skip("Not Implemented")
    def test_get_context_data(self):
        pass


@skip("Not Implemented")
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

from django.test import TestCase  # , TransactionTestCase
from unittest import skip  # @skip("Not Implemented")
from .helper_models import SimpleModelTests, Student, ClassOffer, Payment, Registration, Notify
# from .helper_models import Resource, UserHC, Session, Subject


class PaymentModelTests(SimpleModelTests, TestCase):
    Model = Payment
    repr_dict = {'Payment': '_payment_description'}
    str_list = ['_payment_description']
    defaults = {}


class RegistrationModelTests(SimpleModelTests, TestCase):
    Model = Registration
    repr_dict = {'Registration': 'classoffer', 'User': '_get_full_name', 'Owed': '_pay_report'}
    str_list = ['_get_full_name', 'classoffer', '_pay_report']
    defaults = {}
    related = {'student': Student, 'classoffer': ClassOffer}

    @skip("Not Implemented")
    def test_owed_full_if_no_payment(self):
        pass

    @skip("Not Implemented")
    def test_owed_zero_if_in_person_payment(self):
        pass

    @skip("Not Implemented")
    def test_owed_zero_if_paid_correctly_in_advance(self):
        pass

    @skip("Not Implemented")
    def test_owed_remainder_on_partial_payment(self):
        pass

    @skip("Not Implemented")
    def test_owed_pre_discount_if_paid_after_deadline(self):
        pass

    @skip("Not Implemented")
    def test_first_name(self):
        pass

    @skip("Not Implemented")
    def test_last_name(self):
        pass

    @skip("Not Implemented")
    def test_get_full_name(self):
        pass

    @skip("Not Implemented")
    def test_credit_if_zero(self):
        pass

    @skip("Not Implemented")
    def test_credit_if_some(self):
        pass

    @skip("Not Implemented")
    def test_reg_class_is_subject(self):
        pass

    @skip("Not Implemented")
    def test_session_is_classoffer_session(self):
        pass

    @skip("Not Implemented")
    def test_class_day(self):
        pass

    @skip("Not Implemented")
    def test_start_time(self):
        pass


class NotifyModelTests(TestCase):
    Model = Notify
    repr_dict = {'Notify': 'name'}
    str_list = {}
    # TODO: Figure out values for SimpleModelTests and/or write other tests.

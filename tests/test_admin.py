from django.test import TransactionTestCase, TestCase
from django.contrib import admin as default_admin
from classwork.admin import AdminSessionForm, SessiontAdmin
from classwork.models import Session  # , Subject, ClassOffer, Location, Profile, Registration, Payment
# from django.forms import ValidationError


class AdminSessionManagement(TestCase):
    """ Tests for Session create or modify in the Admin site. """

    def test_admin_uses_correct_admin(self):
        """ The admin site should use the SessiontAdmin for the Session model. """
        # from urls import * # load admin
        registered_admins_dict = default_admin.site._registry
        sess_admin = registered_admins_dict.get(Session, None)
        self.assertTrue(isinstance(sess_admin, SessiontAdmin))

    def test_admin_uses_expected_form(self):
        """ The admin SessiontAdmin utilizes the correct AdminSessionForm. """
        form_class = AdminSessionForm
        current_admin = SessiontAdmin()
        form = current_admin.get_form()
        self.assertTrue(isinstance(form, form_class))

    def test_admin_has_all_model_fields(self):
        """ The admin SessiontAdmin should use all the fields of the Session model. """
        current_admin = SessiontAdmin()
        admin_fields = []
        for ea in current_admin.fields:
            admin_fields.extend(ea)
        for ea in current_admin.fieldsets:
            admin_fields.extend(ea[1].get('fields', []))
        model_fields = [field.name for field in Session._meta.get_fields(include_parents=False)]
        self.assertTupleEqual(tuple(admin_fields), model_fields)

    # def test_admin_can_create_first_session(self):
    #     """ The first Session can be made, even though later Sessions get defaults from existing ones. """
    #     current_admin = SessiontAdmin()
    #     form = current_admin.get_form()

    #     # end test_admin_can_create_first_session

    # def test_validationerror_on_date_conflict(self):
    #     """ Expect a ValidationError when Sessions have overlapping dates. """
    #     current_admin = SessiontAdmin()
    #     form = current_admin.get_form()

    #     day_adjust = -2
    #     last_sess = Session.last_session()
    #     key_day = last_sess.key_day_date + timedelta(days=7*self.duration)
    #     prev_end = last_sess.end_date
    #     error_day = key_day - timedelta(days=7)

    #     self.assertGreater(prev_end, error_day)
    #     sess = self.create_session(
    #         name='overlap_err',
    #         max_day_shift=day_adjust,
    #         key_day_date=error_day
    #         )

        # end test_validationerror_on_date_conflict

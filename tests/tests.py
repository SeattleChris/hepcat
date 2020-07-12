from django.test import TestCase, TransactionTestCase
from .helper import SimpleModelTests
from classwork.models import Location, Resource, SiteContent, Subject, ClassOffer, Profile
from classwork.models import Session, Payment, Registration, Notify
from users.models import UserHC
from datetime import date, timedelta

# Create your tests here.


class SiteContentModelTests(SimpleModelTests, TestCase):
    Model = SiteContent
    repr_dict = {'SiteContent': 'name'}


class LocationModelTests(SimpleModelTests, TestCase):
    Model = Location
    repr_dict = {'Location': 'name', 'Link': 'map_link'}


class ResourceModelTests(SimpleModelTests, TestCase):
    Model = Resource
    repr_dict = {'Resource': 'related_type', 'Type': 'content_type'}
    str_list = ['title', 'related_type', 'content_type']


class SubjectModelTests(SimpleModelTests, TestCase):
    Model = Subject
    repr_dict = {'Subject': 'title', 'Level': 'level', 'Version': 'version'}
    str_list = ['_str_slug']


class ClassOfferModelTests(SimpleModelTests, TestCase):
    Model = ClassOffer
    repr_dict = {'Class Id': 'id', 'Subject': 'subject', 'Session': 'session'}
    str_list = ['subject', 'session']
    defaults = {}


class ProfileModelTests(SimpleModelTests, TestCase):
    Model = Profile
    repr_dict = {'Profile': '_get_full_name', 'User id': 'user_id'}
    str_list = ['_get_full_name']
    defaults = {'email': 'fake@site.com', 'password': '1234', 'first_name': 'fa', 'last_name': 'fake'}

    def setUp(self):
        kwargs = self.defaults.copy()
        # kwargs = {'email': 'fake@site.com', 'password': '1234', 'first_name': 'fa', 'last_name': 'fake'}
        user = UserHC.objects.create_user(**kwargs)
        self.defaults = {}
        self.instance = user.profile  # triggers self.create_model to update this model instead of creating one.


class PaymentModelTests(SimpleModelTests, TestCase):
    Model = Payment
    repr_dict = {'Payment': '_payment_description'}
    str_list = ['_payment_description']
    defaults = {}


USER_DEFAULTS = {'email': 'user_fake@fakesite.com', 'password': '1234', 'first_name': 'f_user', 'last_name': 'fake_y'}


class UserModelTests(SimpleModelTests, TestCase):
    Model = UserHC
    repr_dict = {'UserHC': 'full_name'}
    str_list = ['full_name']
    create_method_name = 'create_user'
    defaults = USER_DEFAULTS.copy()


class UserModelNoNameTests(UserModelTests):
    defaults = {k: v for k, v in USER_DEFAULTS.items() if k not in ('first_name', 'last_name')}


class UserSuperModelTests(UserModelTests):
    create_method_name = 'create_superuser'


class UserSuperModelNoNameTests(UserSuperModelTests):
    defaults = {k: v for k, v in USER_DEFAULTS.items() if k not in ('first_name', 'last_name')}


INITIAL = {
    "name": "May_2020",
    "key_day_date": "2020-04-30",
    "max_day_shift": -2,
    "num_weeks": 5,
    "expire_date": "2020-05-08",
    }


class RegistrationModelTests(SimpleModelTests, TestCase):
    Model = Registration
    repr_dict = {'Registration': 'classoffer', 'User': '_get_full_name', 'Owed': '_pay_report'}
    str_list = ['_get_full_name', 'classoffer', '_pay_report']
    defaults = {}
    related = {'student': Profile, 'classoffer': ClassOffer}


class NotifyModelTests(TestCase):
    Model = Notify
    repr_dict = {'Notify': 'name'}
    str_list = {}
    # TODO: Figure out values for SimpleModelTests and/or write other tests.


class SessionCoverageTests(TransactionTestCase):
    fixtures = ['tests/fixtures/db_basic.json']

    def create_session(self, **kwargs):
        obj = Session.objects.create(**kwargs)
        # obj.refresh_from_db()
        return obj

    def test_create_no_default_functions_no_shift(self):
        """ Session.create works with defined 'key_day_date' and 'publish_date'. """
        key_day = date.today() - timedelta(days=1)
        day_adjust, duration = 0, 5
        publish = key_day - timedelta(days=7*(duration - 1)+1)
        expire = key_day + timedelta(days=8)
        sess = self.create_session(
            name='t1_no_shift',
            key_day_date=key_day,
            max_day_shift=day_adjust,
            num_weeks=duration,
            publish_date=publish,
        )
        self.assertTrue(isinstance(sess, Session))
        self.assertEqual(sess.__str__(), sess.name)
        self.assertEquals(sess.start_date, sess.key_day_date)
        self.assertEquals(sess.publish_date, publish)
        self.assertEquals(sess.expire_date, expire)
        self.assertEquals(sess.end_date, key_day + timedelta(days=7*(duration - 1)))

    def test_session_defaults_on_creation(self):
        """ Session.create works with the date default functions in the model. """
        day_adjust, duration = 0, 5
        key_day = date.fromisoformat(INITIAL['key_day_date']) + timedelta(days=7*INITIAL['num_weeks'])
        new_publish_date = date.fromisoformat(INITIAL['expire_date'])
        expire = key_day + timedelta(days=8)
        end = key_day + timedelta(days=7*(duration - 1))
        sess = self.create_session(
            name='t2_no_shift',
            max_day_shift=day_adjust,
            num_weeks=duration,
        )
        self.assertEquals(sess.key_day_date, key_day)
        self.assertEquals(sess.start_date, key_day)
        self.assertEquals(sess.publish_date, new_publish_date)
        self.assertEquals(sess.expire_date, expire)
        self.assertEquals(sess.end_date, end)
        self.assertEquals(sess.prev_session.name, INITIAL['name'])
        self.assertEquals(sess.prev_session.expire_date, sess.publish_date)
        self.assertLess(sess.prev_session.end_date, sess.start_date)

    def test_create_early_shift_no_skip(self):
        """ Sessions with negative 'max_day_shift' correctly compute their dates. """
        day_adjust, duration = INITIAL['max_day_shift'], INITIAL['num_weeks']
        key_day = date.fromisoformat(INITIAL['key_day_date']) + timedelta(days=7*duration)
        publish = date.fromisoformat(INITIAL['expire_date'])
        expire = key_day + timedelta(days=8)
        start = key_day + timedelta(days=day_adjust)
        end = key_day + timedelta(days=7*(duration - 1))
        sess = self.create_session(
            name='t1_early_shift',
            max_day_shift=day_adjust,
            num_weeks=duration,
        )
        self.assertEquals(sess.key_day_date, key_day)
        self.assertEquals(sess.publish_date, publish)
        self.assertEquals(sess.expire_date, expire)
        self.assertEquals(sess.start_date, start)
        self.assertEquals(sess.start_date, sess.key_day_date + timedelta(days=day_adjust))
        self.assertEquals(sess.end_date, end)
        self.assertEquals(sess.prev_session.expire_date, sess.publish_date)
        self.assertLess(sess.prev_session.end_date, sess.start_date)

    def test_dates_late_shift_no_skip(self):
        """ Sessions with positive 'max_day_shift' correctly compute their dates. """
        day_adjust, duration = 5, INITIAL['num_weeks']
        key_day = date.fromisoformat(INITIAL['key_day_date']) + timedelta(days=7*duration)
        publish = date.fromisoformat(INITIAL['expire_date'])
        expire = key_day + timedelta(days=8+day_adjust)
        start = key_day
        end = key_day + timedelta(days=7*(duration - 1)+day_adjust)
        initial_end = date.fromisoformat(INITIAL['key_day_date']) + timedelta(days=7*(duration - 1))
        sess = self.create_session(
            name='t1_late_shift',
            max_day_shift=day_adjust,
            num_weeks=duration,
        )
        self.assertEquals(sess.key_day_date, key_day)
        self.assertEquals(sess.publish_date, publish)
        self.assertEquals(sess.expire_date, expire)
        self.assertEquals(sess.start_date, start)
        self.assertEquals(sess.end_date, end)
        self.assertLess(sess.prev_session.end_date, sess.start_date)
        self.assertEquals(sess.prev_session.end_date, initial_end)


# end of test.py file

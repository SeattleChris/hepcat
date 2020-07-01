from django.test import TestCase, TransactionTestCase
from classwork.models import Location  # , Resource, SiteContent
from classwork.models import Session  # , Subject, ClassOffer
# from classwork.models import Profile, Payment, Registration, Notify
# from users.models import UserHC
from datetime import date, timedelta
# from django.utils import timezone
# from django.core.urlresolvers import reverse
# from location.forms import WhateverForm

# Create your tests here.
NOW = date.today()
FIRST_KEY_DAY = NOW - timedelta(days=1)

# models test


class LocationCoverageTests(TestCase):
    # fixtures = ['tests/db_basic.json']

    def create_location(self, name="only a test", code="tst", address='123 Some St, #42', zipcode='98112', **kwargs):
        return Location.objects.create(name=name, code=code, address=address, zipcode=zipcode, **kwargs)

    def test_location_creation(self):
        w = self.create_location()
        self.assertTrue(isinstance(w, Location))
        self.assertEqual(w.__str__(), w.name)


class SessionCoverageTests(TransactionTestCase):
    fixtures = ['tests/db_basic.json']

    def create_session(self, **kwargs):
        obj = Session.objects.create(**kwargs)
        obj.refresh_from_db()
        return obj

    def test_session_creation(self):
        day_adjust, duration = 0, 5
        publish = FIRST_KEY_DAY - timedelta(days=7*(duration - 1)+1)
        expire = FIRST_KEY_DAY + timedelta(days=8)
        sess = self.create_session(
            name='t1_no_shift',
            key_day_date=FIRST_KEY_DAY,
            max_day_shift=day_adjust,
            num_weeks=duration,
            publish_date=publish,
        )
        self.assertTrue(isinstance(sess, Session))
        self.assertEqual(sess.__str__(), sess.name)
        self.assertEquals(sess.publish_date, publish)
        self.assertEquals(sess.expire_date, expire)

    def test_session_defaults_on_creation(self):
        day_adjust, duration = 0, 5
        initial = {
            "name": "May_2020",
            "key_day_date": "2020-04-30",
            "max_day_shift": -2,
            "num_weeks": 5,
            "expire_date": "2020-05-08",
        }
        key_day = date.fromisoformat(initial['key_day_date']) + timedelta(days=7*initial['num_weeks'])
        new_publish_date = date.fromisoformat(initial['expire_date'])
        expire = key_day + timedelta(days=8)
        end = key_day + timedelta(days=7*(duration - 1))
        sess = self.create_session(
            name='t2_no_shift',
            max_day_shift=day_adjust,
            num_weeks=duration,
            # key_day_date=FIRST_KEY_DAY,
            # publish_date=publish,
        )
        self.assertEquals(sess.key_day_date, key_day)
        self.assertEquals(sess.start_date, key_day)
        self.assertEquals(sess.publish_date, new_publish_date)
        self.assertEquals(sess.expire_date, expire)
        self.assertEquals(sess.end_date, end)
        self.assertEquals(sess.prev_session.name, 'May_2020')

        # print("============ Second Session Creation ====================")
        # self.assertTrue(isinstance(second_sess, Session))
        # self.assertEqual(second_sess.__str__(), second_sess.name)


# class LocationTests(TestCase):
#     """ The following are just examples. We normally don't have print, or test Django functionality itself. """

#     @classmethod
#     def setUpTestData(cls):
#         print("setUpTestData: Run once to set up non-modified data for all class methods.")
#         cls.first_place = Location.objects.create(
#             name='First Location',
#             code='fl',
#             address='123 Some St, #42',
#             zipcode='98112',
#             map_google='',
#             )
#         # city: use default 'Seattle'
#         # state: use default 'WA'

#     def setUp(self):
#         print("setUp: Run once for every test method to setup clean data.")
#         pass

#     def defaults_used(self):
#         self.assertEquals(self.first_place.city, 'Seattle')
#         self.assertEquals(self.first_place.state, 'WA')

#     def test_false_is_false(self):
#         print("Method: test_false_is_false.")
#         self.assertFalse(False)

#     def test_false_is_true(self):
#         print("Method: test_false_is_true.")
#         self.assertTrue(False)

#     def test_one_plus_one_equals_two(self):
#         print("Method: test_one_plus_one_equals_two.")
#         self.assertEqual(1 + 1, 2)


# class GeneralModelTests(TestCase):

#     def setUp(self):
#         """ Initial models needed in the database. """
#         day_adjust, duration = 0, 5
#         publish = FIRST_KEY_DAY - timedelta(days=7*(duration - 1)+1)
#         try:
#             self.first_sess = Session.objects.create(
#                 name='t1_no_shift',
#                 key_day_date=FIRST_KEY_DAY,
#                 max_day_shift=day_adjust,
#                 num_weeks=duration,
#                 publish_date=publish,
#                 )
#         except TypeError as e:
#             print(f"TEST SETUP _1_ TYPEERROR EXCEPTION: {e} ")
#             raise e
#         print(f'TEST SETUP: First Session made: {self.first_sess} ')
#         print(getattr(self.first_sess, 'key_day_date', 'NOT FOUND KEY DAY'))

#     def test_01_setup(self):
#         """ Did the setup happen? """
#         self.assertIsNotNone(NOW)
#         self.assertIsInstance(NOW, date)
#         self.assertIsInstance(FIRST_KEY_DAY, date)
#         self.assertIsInstance(self.first_sess, Session)
#         self.assertEquals(self.first_sess.name, 't1_no_shift')


# end of test.py file

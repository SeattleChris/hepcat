from django.test import TestCase, TransactionTestCase
# from classwork.models import Session, Subject, ClassOffer
from classwork.models import Location  # , Resource, SiteContent
# from classwork.models import Profile, Payment, Registration, Notify
# from users.models import UserHC
from datetime import date, timedelta

# Create your tests here.
NOW = date.today()
FIRST_KEY_DAY = NOW - timedelta(days=1)


class LocationTests(TestCase):
    """ The following are just examples. We normally don't have print, or test Django functionality itself. """

    @classmethod
    def setUpTestData(cls):
        print("setUpTestData: Run once to set up non-modified data for all class methods.")
        cls.first_place = Location.objects.create(
            name='First Location',
            code='fl',
            address='123 Some St, #42',
            zipcode='98112',
            map_google='',
            )
        # city: use default 'Seattle'
        # state: use default 'WA'

    def setUp(self):
        print("setUp: Run once for every test method to setup clean data.")
        pass

    def defaults_used(self):
        self.assertEquals(self.first_place.city, 'Seattle')
        self.assertEquals(self.first_place.state, 'WA')

    def test_false_is_false(self):
        print("Method: test_false_is_false.")
        self.assertFalse(False)

    def test_false_is_true(self):
        print("Method: test_false_is_true.")
        self.assertTrue(False)

    def test_one_plus_one_equals_two(self):
        print("Method: test_one_plus_one_equals_two.")
        self.assertEqual(1 + 1, 2)


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

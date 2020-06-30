from django.test import TestCase, TransactionTestCase
from classwork.models import Location, Session  # , Subject, ClassOffer, Profile, Registration, Payment
from datetime import date, timedelta

# Create your tests here.
NOW = date.today()
FIRST_KEY_DAY = NOW - timedelta(days=1)


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

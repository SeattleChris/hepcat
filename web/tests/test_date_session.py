from django.test import TestCase, TransactionTestCase
from classwork.models import Location, Session  # , Subject, ClassOffer, Profile, Registration, Payment
from datetime import date, timedelta

# Create your tests here.
NOW = date.today()
FIRST_KEY_DAY = NOW - timedelta(days=1)


class SessionModelTests(TransactionTestCase):

    # def setUp(self):
    #     """ Initial models needed in the database. """
    #     day_adjust, duration = 0, 5
    #     publish = FIRST_KEY_DAY - timedelta(days=7*(duration - 1)+1)
    #     try:
    #         self.first_sess = Session.objects.create(
    #             name='t1_no_shift',
    #             key_day_date=FIRST_KEY_DAY,
    #             max_day_shift=day_adjust,
    #             num_weeks=duration,
    #             publish_date=publish,
    #             )
    #     except TypeError as e:
    #         print(f"TEST SETUP _1_ TYPEERROR EXCEPTION: {e} ")
    #         raise e
    #     print(f'TEST SETUP: First Session made: {self.first_sess} ')
    #     print(getattr(self.first_sess, 'key_day_date', 'NOT FOUND KEY DAY'))
    #     print('------------ mid setUp -------------------')
    #     try:
    #         self.second_sess = Session.objects.create(
    #             name='t2_no_shift',
    #             max_day_shift=day_adjust,
    #             num_weeks=duration,
    #             )
    #     except TypeError as e:
    #         from pprint import pprint
    #         print(f"TEST SETUP _2_ TYPEERROR EXCEPTION: {e} ")
    #         pprint(dir(e))
    #         print('-------------------------------------')
    #         raise e
    #     print(f'TEST SETUP Second made: {self.second_sess} ')
    #     print('TEST SETUP END')

    # def test_01_setup(self):
    #     """ Did the setup happen? """
    #     self.assertIsNotNone(NOW)
    #     self.assertIsInstance(NOW, date)
    #     self.assertIsInstance(FIRST_KEY_DAY, date)
    #     self.assertIsInstance(self.first_sess, Session)
    #     self.assertIsInstance(self.second_sess, Session)

    def test_dates_01_no_shift_no_skips(self):
        """ The end date should be when the last class of this session is held.
            First, this depends on what is the latest a class could start:
            If max_day_shift is negative or 0, then start on key_day_date.
            If it is positive, then we start that many days after key_date.
            Assume no skipped weeks and no break weeks for this test.
            Therefore, the end_date will be duration number of weeks after this latest starting class.
            Testing: start_date, end_date, key_day_date, publish_date, expire_date
        """
        day_adjust, duration = 0, 5
        first_expire = FIRST_KEY_DAY + timedelta(days=8)
        last_class = FIRST_KEY_DAY + timedelta(days=7*(duration - 1))
        # last_class = last_class + timedelta(days=day_adjust) if day_adjust > 0 else last_class
        second_key_day = FIRST_KEY_DAY + timedelta(days=7*duration)
        publish = FIRST_KEY_DAY - timedelta(days=7*(duration - 1)+1)
        test_first_sess = Session.objects.create(
            name='test_1_no_shift',
            key_day_date=FIRST_KEY_DAY,
            max_day_shift=day_adjust,
            num_weeks=duration,
            publish_date=publish,
            )
        test_second_sess = Session.objects.create(
            name='test_2_no_shift',
            max_day_shift=day_adjust,
            num_weeks=duration,
            )
        test_first_sess = Session.objects.get(name='test_1_no_shift')
        test_second_sess = Session.objects.get(name='test_2_no_shift')
        self.assertEquals(test_first_sess.start_date, FIRST_KEY_DAY)
        self.assertEquals(test_first_sess.start_date, test_first_sess.key_day_date)
        self.assertEquals(test_first_sess.end_date, last_class)
        self.assertEquals(test_first_sess.expire_date, first_expire)
        self.assertEquals(test_second_sess.key_day_date, second_key_day)
        self.assertEquals(test_second_sess.publish_date, first_expire)
        self.assertGreater(test_first_sess.end_date, test_second_sess.start_date)

    # def test_dates_early_shift_no_skips(self):
    #     """ The end date should be when the last class of this session is held.
    #         First, this depends on what is the latest a class could start:
    #         If max_day_shift is negative or 0, then start on key_day_date.
    #         If it is positive, then we start that many days after key_date.
    #         Assume no skipped weeks and no break weeks for this test.
    #         Therefore, the end_date will be duration number of weeks after this latest starting class.
    #         Testing: start_date, end_date, key_day_date, publish_date, expire_date
    #     """
    #     now = date.today()
    #     key_day = now - timedelta(days=1)
    #     day_adjust = -2
    #     duration = 5
    #     first_day = key_day + timedelta(days=day_adjust)
    #     publish = key_day - timedelta(days=7*(duration - 1)+1)
    #     first_expire = key_day + timedelta(days=8)
    #     last_class = key_day + timedelta(days=7*(duration - 1))
    #     last_class = last_class + timedelta(days=day_adjust) if day_adjust > 0 else last_class
    #     test_first_sess = Session.objects.create(
    #         name='test_1_early',
    #         key_day_date=key_day,
    #         max_day_shift=day_adjust,
    #         num_weeks=duration,
    #         publish_date=publish,
    #         )
    #     second_key_day = key_day + timedelta(days=7*duration)
    #     test_second_sess = Session.objects.create(
    #         name='test_2_early',
    #         max_day_shift=day_adjust,
    #         num_weeks=duration,
    #     )
    #     self.assertEquals(test_first_sess.start_date, first_day)
    #     self.assertEquals(test_first_sess.key_day_date, key_day)
    #     self.assertEquals(test_first_sess.end_date, last_class)
    #     self.assertEquals(test_first_sess.expire_date, first_expire)
    #     self.assertEquals(test_second_sess.key_day_date, second_key_day)
    #     self.assertEquals(test_second_sess.publish_date, first_expire)
    #     self.assertGreater(test_first_sess.end_date, test_second_sess.start_date)

    # def test_dates_late_shift_no_skips(self):
    #     """ The end date should be when the last class of this session is held.
    #         First, this depends on what is the latest a class could start:
    #         If max_day_shift is negative or 0, then start on key_day_date.
    #         If it is positive, then we start that many days after key_date.
    #         Assume no skipped weeks and no break weeks for this test.
    #         Therefore, the end_date will be duration number of weeks after this latest starting class.
    #         Testing: start_date, end_date, key_day_date, publish_date, expire_date
    #     """
    #     now = date.today()
    #     key_day = now - timedelta(days=1)
    #     day_adjust = 4
    #     duration = 5
    #     # first_day = key_day
    #     publish = key_day - timedelta(days=7*(duration - 1)+1)
    #     first_expire = key_day + timedelta(days=8+day_adjust)
    #     last_class = key_day + timedelta(days=7*(duration - 1))
    #     last_class = last_class + timedelta(days=day_adjust) if day_adjust > 0 else last_class
    #     test_first_sess = Session.objects.create(
    #         name='test_1_late',
    #         key_day_date=key_day,
    #         max_day_shift=day_adjust,
    #         num_weeks=duration,
    #         publish_date=publish,
    #         )
    #     second_key_day = key_day + timedelta(days=7*duration)
    #     test_second_sess = Session.objects.create(
    #         name='test_2_late',
    #         max_day_shift=day_adjust,
    #         num_weeks=duration,
    #     )
    #     self.assertEquals(test_first_sess.start_date, key_day)
    #     self.assertEquals(test_first_sess.key_day_date, key_day)
    #     self.assertEquals(test_first_sess.end_date, last_class)
    #     self.assertEquals(test_first_sess.expire_date, first_expire)
    #     self.assertEquals(test_second_sess.key_day_date, second_key_day)
    #     self.assertEquals(test_second_sess.publish_date, first_expire)
    #     self.assertGreater(test_first_sess.end_date, test_second_sess.start_date)

    # def test_dates_skips_key_date_early_shift(self):
    #     """ The end date should be when the last class of this session is held.
    #         First, this depends on what is the latest a class could start:
    #         If max_day_shift is negative or 0, then start on key_day_date.
    #         If it is positive, then we start that many days after key_date.
    #         Assume skipped weeks only effects the key_day class day.
    #         Therefore, the end_date will be duration number of weeks after this latest starting class.
    #         Testing: start_date, end_date, key_day_date, publish_date, expire_date
    #     """
    #     now = date.today()
    #     key_day = now - timedelta(days=1)
    #     day_adjust = -2
    #     duration = 5
    #     first_day = key_day + timedelta(days=day_adjust)
    #     skips = 1
    #     publish = key_day - timedelta(days=7*(duration - 1)+1)
    #     first_expire = key_day + timedelta(days=8)
    #     last_class = key_day + timedelta(days=7*(duration + skips - 1))
    #     last_class = last_class + timedelta(days=day_adjust) if day_adjust > 0 else last_class
    #     test_first_sess = Session.objects.create(
    #         name='test_1_early',
    #         key_day_date=key_day,
    #         max_day_shift=day_adjust,
    #         num_weeks=duration,
    #         skip_weeks=skips,
    #         flip_last_day=False,
    #         publish_date=publish,
    #         )
    #     second_key_day = key_day + timedelta(days=7*(duration + skips))
    #     second_skips = 3
    #     third_key_day = second_key_day + timedelta(days=7*(duration + second_skips))
    #     test_second_sess = Session.objects.create(
    #         name='test_2_early',
    #         max_day_shift=day_adjust,
    #         num_weeks=duration,
    #         skip_weeks=second_skips,
    #         flip_last_day=False,
    #         )
    #     test_third_sess = Session.objects.create(
    #         name='test_3_early',
    #         max_day_shift=day_adjust,
    #         num_weeks=duration,
    #         skip_weeks=0,
    #         )
    #     self.assertEquals(test_first_sess.start_date, first_day)
    #     self.assertEquals(test_first_sess.key_day_date, key_day)
    #     self.assertEquals(test_first_sess.end_date, last_class)
    #     self.assertEquals(test_first_sess.expire_date, first_expire)
    #     self.assertEquals(test_second_sess.key_day_date, second_key_day)
    #     self.assertEquals(test_second_sess.publish_date, first_expire)
    #     self.assertEquals(test_third_sess.publish_date, test_second_sess.expire_date)
    #     self.assertEquals(test_third_sess.key_day_date, third_key_day)
    #     self.assertGreater(test_first_sess.end_date, test_second_sess.start_date)
    #     self.assertGreater(test_second_sess.end_date, test_third_sess.start_date)

    # def test_dates_skips_key_date_late_shift(self):
    #     """ The end date should be when the last class of this session is held.
    #         First, this depends on what is the latest a class could start:
    #         If max_day_shift is negative or 0, then start on key_day_date.
    #         If it is positive, then we start that many days after key_date.
    #         Assume skipped weeks only effects the key_day class day.
    #         Therefore, the end_date will be duration number of weeks after this latest starting class.
    #         Testing: start_date, end_date, key_day_date, publish_date, expire_date
    #     """
    #     now = date.today()
    #     key_day = now - timedelta(days=1)
    #     day_adjust = 4
    #     duration = 5
    #     # first_day = key_day
    #     skips = 1
    #     publish = key_day - timedelta(days=7*(duration - 1)+1)
    #     first_expire = key_day + timedelta(days=8+day_adjust)
    #     last_class = key_day + timedelta(days=7*(duration + skips - 1))
    #     # last_class is on weekday of key_day because skip weeks were only on the key_day.
    #     test_first_sess = Session.objects.create(
    #         name='test_1_late',
    #         key_day_date=key_day,
    #         max_day_shift=day_adjust,
    #         num_weeks=duration,
    #         skip_weeks=skips,
    #         flip_last_day=True,
    #         publish_date=publish,
    #         )
    #     second_key_day = key_day + timedelta(days=7*(duration + skips))
    #     second_skips = 3
    #     second_last_class = second_key_day + timedelta(days=7*(duration + second_skips - 1))
    #     # second_last_class is also on the weekday of key_day because skips are only on key_day.
    #     third_key_day = second_key_day + timedelta(days=7*(duration + second_skips))
    #     test_second_sess = Session.objects.create(
    #         name='test_2_late',
    #         max_day_shift=day_adjust,
    #         num_weeks=duration,
    #         skip_weeks=second_skips,
    #         flip_last_day=True,
    #         )
    #     test_third_sess = Session.objects.create(
    #         name='test_3_late',
    #         max_day_shift=day_adjust,
    #         num_weeks=duration,
    #         skip_weeks=0,
    #         )
    #     self.assertEquals(test_first_sess.start_date, key_day)
    #     self.assertEquals(test_first_sess.key_day_date, key_day)
    #     self.assertEquals(test_first_sess.end_date, last_class)
    #     self.assertEquals(test_first_sess.expire_date, first_expire)
    #     self.assertEquals(test_second_sess.key_day_date, second_key_day)
    #     self.assertEquals(test_second_sess.start_date, second_key_day)
    #     self.assertEquals(test_second_sess.end_date, second_last_class)
    #     self.assertEquals(test_second_sess.publish_date, first_expire)
    #     self.assertEquals(test_third_sess.publish_date, test_second_sess.expire_date)
    #     self.assertEquals(test_third_sess.key_day_date, third_key_day)
    #     self.assertGreater(test_first_sess.end_date, test_second_sess.start_date)
    #     self.assertGreater(test_second_sess.end_date, test_third_sess.start_date)

    # def test_end_date_skips_other_date_early_shift(self):
    #     """ The end date should be when the last class of this session is held.
    #         First, this depends on what is the latest a class could start:
    #         If max_day_shift is negative or 0, then start on key_day_date.
    #         If it is positive, then we start that many days after key_date.
    #         Assume skipped weeks only effects the non-key_day class day.
    #         Therefore, the end_date will be duration number of weeks after this latest starting class.
    #         Testing: start_date, end_date, key_day_date, publish_date, expire_date
    #     """
    #     now = date.today()
    #     key_day = now - timedelta(days=1)
    #     day_adjust = -2
    #     duration = 5
    #     first_day = key_day + timedelta(days=day_adjust)
    #     skips = 1
    #     publish = key_day - timedelta(days=7*(duration - 1)+1)
    #     first_expire = key_day + timedelta(days=8)
    #     last_class = key_day + timedelta(days=7*(duration - 1))
    #     last_class += timedelta(days=day_adjust+7*skips)
    #     # Since skips are only on non-key_day, the other days move to the last class.
    #     test_first_sess = Session.objects.create(
    #         name='test_1_early',
    #         key_day_date=key_day,
    #         max_day_shift=day_adjust,
    #         num_weeks=duration,
    #         skip_weeks=skips,
    #         flip_last_day=True,
    #         publish_date=publish,
    #         )
    #     second_key_day = key_day + timedelta(days=7*(duration))
    #     # the one-week skip from first session did not affect the second session key day
    #     second_skips = 3
    #     second_last_class = key_day + timedelta(days=7*(duration - 1))
    #     second_last_class += timedelta(days=day_adjust+7*second_skips)
    #     third_key_day = second_key_day + timedelta(days=7*(duration + second_skips - 1))
    #     # Technically when skips not on key_day, the following key_day still moves by one less than skipped weeks
    #     # Typically there is 0 or 1 skipped weeks, but could be more so should be "one less than skips if any skips"
    #     test_second_sess = Session.objects.create(
    #         name='test_2_early',
    #         max_day_shift=day_adjust,
    #         num_weeks=duration,
    #         skip_weeks=second_skips,
    #         flip_last_day=True,
    #         )
    #     test_third_sess = Session.objects.create(
    #         name='test_3_early',
    #         max_day_shift=day_adjust,
    #         num_weeks=duration,
    #         skip_weeks=0,
    #         )
    #     self.assertEquals(test_first_sess.start_date, first_day)
    #     self.assertEquals(test_first_sess.key_day_date, key_day)
    #     self.assertEquals(test_first_sess.end_date, last_class)
    #     self.assertEquals(test_first_sess.expire_date, first_expire)
    #     self.assertEquals(test_second_sess.key_day_date, second_key_day)
    #     self.assertEquals(test_second_sess.end_date, second_last_class)
    #     self.assertEquals(test_second_sess.publish_date, first_expire)
    #     self.assertEquals(test_third_sess.key_day_date, third_key_day)
    #     self.assertEquals(test_third_sess.publish_date, test_second_sess.expire_date)
    #     self.assertGreater(test_first_sess.end_date, test_second_sess.start_date)
    #     self.assertGreater(test_second_sess.end_date, test_third_sess.start_date)

    # def test_end_date_skips_other_date_late_shift(self):
    #     """ The end date should be when the last class of this session is held.
    #         First, this depends on what is the latest a class could start:
    #         If max_day_shift is negative or 0, then start on key_day_date.
    #         If it is positive, then we start that many days after key_date.
    #         Assume skipped weeks only effects the non-key_day class day.
    #         Therefore, the end_date will be duration number of weeks after this latest starting class.
    #         Testing: start_date, end_date, key_day_date, publish_date, expire_date
    #     """
    #     now = date.today()
    #     key_day = now - timedelta(days=1)
    #     day_adjust = 4
    #     duration = 5
    #     # first_day = key_day
    #     skips = 1
    #     publish = key_day - timedelta(days=7*(duration - 1)+1)
    #     first_expire = key_day + timedelta(days=8+day_adjust)
    #     last_class = key_day + timedelta(days=7*(duration - 1))
    #     last_class = last_class + timedelta(days=day_adjust) if day_adjust > 0 else last_class
    #     last_class += timedelta(days=7*skips)
    #     test_first_sess = Session.objects.create(
    #         name='test_1_late',
    #         key_day_date=key_day,
    #         max_day_shift=day_adjust,
    #         num_weeks=duration,
    #         skip_weeks=skips,
    #         flip_last_day=False,
    #         publish_date=publish,
    #         )
    #     second_key_day = key_day + timedelta(days=7*(duration + skips - 1))
    #     # Technically when skips not on key_day, the following key_day still moves by one less than skipped weeks
    #     # Typically there is 0 or 1 skipped weeks, but could be more so should be "one less than skips if any skips"
    #     second_skips = 3
    #     # second_first_day = last_class + timedelta(days=7)
    #     # self.assertEquals(test_second_sess.start_date, second_first_day)
    #     # Since no break weeks & same day_adjust, second_last_class should match continue_last, from first last_class
    #     continue_last = last_class + timedelta(days=7*(duration + second_skips - 1))
    #     second_last_class = second_key_day + timedelta(days=day_adjust+7*(duration + second_skips - 1))
    #     third_key_day = second_key_day + timedelta(days=7*(duration + second_skips - 1))
    #     # third_key_day has minus one because: no break weeks, and second session skip days not on key_day
    #     test_second_sess = Session.objects.create(
    #         name='test_2_late',
    #         max_day_shift=day_adjust,
    #         num_weeks=duration,
    #         skip_weeks=second_skips,
    #         flip_last_day=False,
    #         )
    #     test_third_sess = Session.objects.create(
    #         name='test_3_late',
    #         max_day_shift=day_adjust,
    #         num_weeks=duration,
    #         skip_weeks=0,
    #         )
    #     self.assertEquals(test_first_sess.start_date, key_day)
    #     self.assertEquals(test_first_sess.key_day_date, key_day)
    #     self.assertEquals(test_first_sess.end_date, last_class)
    #     self.assertEquals(test_first_sess.expire_date, first_expire)
    #     self.assertEquals(test_second_sess.start_date, second_key_day)
    #     self.assertEquals(test_second_sess.key_day_date, second_key_day)
    #     self.assertEquals(test_second_sess.end_date, second_last_class)
    #     self.assertEquals(test_second_sess.end_date, continue_last)
    #     self.assertEquals(test_second_sess.publish_date, first_expire)
    #     self.assertEquals(test_third_sess.publish_date, test_second_sess.expire_date)
    #     self.assertEquals(test_third_sess.key_day_date, third_key_day)
    #     self.assertGreater(test_first_sess.end_date, test_second_sess.start_date)
    #     self.assertGreater(test_second_sess.end_date, test_third_sess.start_date)

# end class SessionModelTests


# end of test.py file

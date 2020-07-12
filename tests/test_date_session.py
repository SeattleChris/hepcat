from django.test import TransactionTestCase  # , TestCase
# from django.forms import ValidationError
from classwork.models import Session  # , Subject, ClassOffer, Location, Profile, Registration, Payment
# from classwork.admin import AdminSessionForm, SessiontAdmin
# from django.contrib import admin as default_admin
from datetime import date, timedelta

INITIAL = {
    "name": "May_2020",
    "key_day_date": "2020-04-30",
    "max_day_shift": -2,
    "num_weeks": 5,
    "expire_date": "2020-05-08",
    }
early_no_skip = {
    "name": "early_no_skip",
    "max_day_shift": -2,
    "num_weeks": 5,
    "key_day_date": "2020-06-04",
    "skip_weeks": 0,
    "flip_last_day": False,
    "break_weeks": 0,
    "publish_date": "2020-05-08",
    "expire_date": "2020-06-12",
    }
early1_oth_skip = {
    "name": "early1_oth_skip",
    "key_day_date": "2020-06-04",
    "max_day_shift": -2,
    "num_weeks": 5,
    "skip_weeks": 1,
    "flip_last_day": True,
    "break_weeks": 0,
    "publish_date": "2020-05-08",
    "expire_date": "2020-06-12",
    }
# no_skip = 'tests/fixtures/db_early_no_skip_session.json'  # max_day_shift=-2, skip_weeks=0, num_weeks=5
# oth_skip = 'tests/fixtures/db_early1_oth_skip_session.json'  # max_day_shift=-2, skip_weeks=1, flip_last_day=True, num_weeks=5
# Create your tests here.


class NoSkipToOneSkipSessionDates(TransactionTestCase):
    fixtures = ['tests/fixtures/db_basic.json', 'tests/fixtures/db_early_no_skip_session.json']
    skips = 1
    duration = 5

    def create_session(self, **kwargs):
        kwargs['num_weeks'] = self.duration  # if 'num_weeks' not in kwargs else kwargs['num_weeks']
        kwargs['skip_weeks'] = self.skips    # if 'skip_weeks' not in kwargs else kwargs['skip_weeks']
        obj = Session.objects.create(**kwargs)
        # TODO: Handle if creating object raises a ValidationError, as sometimes expected.
        return obj

    def test_skip_key_date_early_shift(self):
        """ Session with early shift and 1 skip week on the key day. """
        day_adjust = -2
        last_sess = Session.last_session()
        key_day = last_sess.key_day_date + timedelta(days=7*self.duration)
        prev_end = last_sess.end_date
        publish = date.fromisoformat(INITIAL['expire_date']) + timedelta(days=7*self.duration)
        expire = key_day + timedelta(days=8)
        start = key_day + timedelta(days=day_adjust)
        end = key_day + timedelta(days=7*(self.duration + self.skips - 1))
        # prev_end = date.fromisoformat(INITIAL['key_day_date']) + timedelta(days=7*(2 * self.duration - 1))
        sess = self.create_session(
            name='early_key_skip',
            max_day_shift=day_adjust,
            flip_last_day=False,
            )
        self.assertEquals(sess.key_day_date, key_day)
        self.assertEquals(sess.publish_date, publish)
        self.assertEquals(sess.expire_date, expire)
        self.assertEquals(sess.start_date, start)
        self.assertEquals(sess.end_date, end)
        sess.save(with_clean=True)
        self.assertEquals(sess.prev_session.expire_date, sess.publish_date)
        self.assertLess(sess.prev_session.end_date, sess.start_date)
        self.assertEquals(sess.prev_session.end_date, prev_end)

    def test_skip_key_date_late_shift(self):
        """ Session with late shift and 1 skip week on the key day, flipping last class day. """
        day_adjust = 5
        # key_day = date.fromisoformat(INITIAL['key_day_date']) + timedelta(days=7*2*self.duration)
        last_sess = Session.last_session()
        key_day = last_sess.key_day_date + timedelta(days=7*self.duration)
        publish = date.fromisoformat(INITIAL['expire_date']) + timedelta(days=7*self.duration)
        expire = key_day + timedelta(days=8+day_adjust)
        start = key_day
        end = key_day + timedelta(days=7*(self.duration + self.skips - 1))
        # prev_end = date.fromisoformat(INITIAL['key_day_date']) + timedelta(days=7*(2 * self.duration - 1))
        prev_end = last_sess.end_date
        sess = self.create_session(
            name='late_key_skip',
            max_day_shift=day_adjust,
            flip_last_day=True,
            )
        self.assertEquals(sess.key_day_date, key_day)
        self.assertEquals(sess.publish_date, publish)
        self.assertEquals(sess.expire_date, expire)
        self.assertEquals(sess.start_date, start)
        self.assertEquals(sess.end_date, end)
        sess.save(with_clean=True)
        self.assertEquals(sess.prev_session.expire_date, sess.publish_date)
        self.assertLess(sess.prev_session.end_date, sess.start_date)
        self.assertEquals(sess.prev_session.end_date, prev_end)

    def test_skip_other_date_early_shift(self):
        """ Session with early shift and 1 skip week NOT on the key day, flipping last class day. """
        day_adjust = -2
        last_sess = Session.last_session()
        key_day = last_sess.key_day_date + timedelta(days=7*self.duration)
        # key_day = date.fromisoformat(INITIAL['key_day_date']) + timedelta(days=7*2*self.duration)
        publish = date.fromisoformat(INITIAL['expire_date']) + timedelta(days=7*self.duration)
        expire = key_day + timedelta(days=8)
        start = key_day + timedelta(days=day_adjust)
        end = key_day + timedelta(days=7*(self.duration + self.skips - 1)+day_adjust)
        # prev_end = date.fromisoformat(INITIAL['key_day_date']) + timedelta(days=7*(2 * self.duration - 1))
        prev_end = last_sess.end_date
        sess = self.create_session(
            name='early2_oth_skip',
            max_day_shift=day_adjust,
            flip_last_day=True,
            )
        sess.refresh_from_db()
        self.assertEquals(sess.key_day_date, key_day)
        self.assertEquals(sess.publish_date, publish)
        self.assertEquals(sess.expire_date, expire)
        self.assertEquals(sess.start_date, start)
        self.assertEquals(sess.end_date, end)
        sess.save(with_clean=True)
        self.assertEquals(sess.prev_session.expire_date, sess.publish_date)
        self.assertLess(sess.prev_session.end_date, sess.start_date)
        self.assertEquals(sess.prev_session.end_date, prev_end)

    def test_skip_other_date_late_shift(self):
        """ Session with late shift and 1 skip week NOT on the key_day. """
        day_adjust = 5
        last_sess = Session.last_session()
        key_day = last_sess.key_day_date + timedelta(days=7*self.duration)
        # key_day = date.fromisoformat(INITIAL['key_day_date']) + timedelta(days=7*2*self.duration)
        publish = date.fromisoformat(INITIAL['expire_date']) + timedelta(days=7*self.duration)
        expire = key_day + timedelta(days=8+day_adjust)
        start = key_day
        end = key_day + timedelta(days=7*(self.duration + self.skips - 1)+day_adjust)
        # prev_end = date.fromisoformat(INITIAL['key_day_date']) + timedelta(days=7*(2 * self.duration - 1))
        prev_end = last_sess.end_date
        sess = self.create_session(
            name='late_oth_skip',
            max_day_shift=day_adjust,
            flip_last_day=False,
            )
        sess.refresh_from_db()
        self.assertEquals(sess.key_day_date, key_day)
        self.assertEquals(sess.publish_date, publish)
        self.assertEquals(sess.expire_date, expire)
        self.assertEquals(sess.start_date, start)
        self.assertEquals(sess.end_date, end)
        sess.save(with_clean=True)
        self.assertEquals(sess.prev_session.expire_date, sess.publish_date)
        self.assertLess(sess.prev_session.end_date, sess.start_date)
        self.assertEquals(sess.prev_session.end_date, prev_end)


class OneOtherSkipEarlyToOneSkip(NoSkipToOneSkipSessionDates):
    fixtures = ['tests/fixtures/db_basic.json', 'tests/fixtures/db_early1_oth_skip_session.json']
    skips = 1
    duration = 5


class OneOtherSkipEarlyToThreeSkip(NoSkipToOneSkipSessionDates):
    fixtures = ['tests/fixtures/db_basic.json', 'tests/fixtures/db_early1_oth_skip_session.json']
    skips = 3
    duration = 5


# class SessionDateAfterEarlyOtherSkip(TransactionTestCase):
#     fixtures = ['tests/fixtures/db_basic.json', 'tests/fixtures/db_early1_oth_skip_session.json']

#     def create_session(self, **kwargs):
#         obj = self.create_session(**kwargs)
#         # obj.refresh_from_db()
#         return obj

#     def test_skip_key_date_early_shift(self):
#         """ Session with early shift and 1 skip week on the key day. """
#         day_adjust = -2
#         key_day = date.fromisoformat(INITIAL['key_day_date']) + timedelta(days=7*2*self.duration)
#         publish = date.fromisoformat(INITIAL['expire_date']) + timedelta(days=7*duration)
#         expire = key_day + timedelta(days=8)
#         start = key_day + timedelta(days=day_adjust)
#         end = key_day + timedelta(days=7*(duration + skips - 1))
#         prev_end = date.fromisoformat(INITIAL['key_day_date']) + timedelta(days=7*(2 * duration - 1))
#         sess = Session.objects.create(
#             name='early_key_skip',
#             max_day_shift=day_adjust,
#             num_weeks=duration,
#             skip_weeks=skips,
#             flip_last_day=False,
#             )
#         self.assertEquals(sess.key_day_date, key_day)
#         self.assertEquals(sess.publish_date, publish)
#         self.assertEquals(sess.expire_date, expire)
#         self.assertEquals(sess.start_date, start)
#         self.assertEquals(sess.end_date, end)
#         self.assertEquals(sess.prev_session.expire_date, sess.publish_date)
#         self.assertLess(sess.prev_session.end_date, sess.start_date)
#         self.assertEquals(sess.prev_session.end_date, prev_end)

#     def test_dates_skips_key_date_late_shift(self):
#         """ Session with late shift and 1 skip week on the key day, flipping last class day. """
#         skips, day_adjust, duration = 1, 5, INITIAL['num_weeks']
#         key_day = date.fromisoformat(INITIAL['key_day_date']) + timedelta(days=7*2*duration)
#         publish = date.fromisoformat(INITIAL['expire_date']) + timedelta(days=7*duration)
#         expire = key_day + timedelta(days=8+day_adjust)
#         start = key_day
#         end = key_day + timedelta(days=7*(duration + skips - 1))
#         prev_end = date.fromisoformat(INITIAL['key_day_date']) + timedelta(days=7*(2 * duration - 1))
#         sess = Session.objects.create(
#             name='late_key_skip',
#             max_day_shift=day_adjust,
#             num_weeks=duration,
#             skip_weeks=skips,
#             flip_last_day=True,
#             )
#         self.assertEquals(sess.key_day_date, key_day)
#         self.assertEquals(sess.publish_date, publish)
#         self.assertEquals(sess.expire_date, expire)
#         self.assertEquals(sess.start_date, start)
#         self.assertEquals(sess.end_date, end)
#         self.assertEquals(sess.prev_session.expire_date, sess.publish_date)
#         self.assertLess(sess.prev_session.end_date, sess.start_date)
#         self.assertEquals(sess.prev_session.end_date, prev_end)

#     def test_dates_skips_other_date_early_shift(self):
#         """ Session with early shift and 1 skip week NOT on the key day, flipping last class day. """
#         skips, day_adjust, duration = 1, -2, INITIAL['num_weeks']
#         key_day = date.fromisoformat(INITIAL['key_day_date']) + timedelta(days=7*2*duration)
#         publish = date.fromisoformat(INITIAL['expire_date']) + timedelta(days=7*duration)
#         expire = key_day + timedelta(days=8)
#         start = key_day + timedelta(days=day_adjust)
#         end = key_day + timedelta(days=7*(duration + skips - 1)+day_adjust)
#         prev_end = date.fromisoformat(INITIAL['key_day_date']) + timedelta(days=7*(2 * duration - 1))
#         sess = Session.objects.create(
#             name='early2_oth_skip',
#             max_day_shift=day_adjust,
#             num_weeks=duration,
#             skip_weeks=skips,
#             flip_last_day=True,
#             )
#         self.assertEquals(sess.key_day_date, key_day)
#         self.assertEquals(sess.publish_date, publish)
#         self.assertEquals(sess.expire_date, expire)
#         self.assertEquals(sess.start_date, start)
#         self.assertEquals(sess.end_date, end)
#         self.assertEquals(sess.prev_session.expire_date, sess.publish_date)
#         self.assertLess(sess.prev_session.end_date, sess.start_date)
#         self.assertEquals(sess.prev_session.end_date, prev_end)

#     def test_dates_skips_other_date_late_shift(self):
#         """ Session with late shift and 1 skip week NOT on the key_day. """
#         skips, day_adjust, duration = 1, 5, INITIAL['num_weeks']
#         key_day = date.fromisoformat(INITIAL['key_day_date']) + timedelta(days=7*2*duration)
#         publish = date.fromisoformat(INITIAL['expire_date']) + timedelta(days=7*duration)
#         expire = key_day + timedelta(days=8+day_adjust)
#         start = key_day
#         end = key_day + timedelta(days=7*(duration + skips - 1)+day_adjust)
#         prev_end = date.fromisoformat(INITIAL['key_day_date']) + timedelta(days=7*(2 * duration - 1))
#         sess = Session.objects.create(
#             name='late_oth_skip',
#             max_day_shift=day_adjust,
#             num_weeks=duration,
#             skip_weeks=skips,
#             flip_last_day=False,
#             )
#         self.assertEquals(sess.key_day_date, key_day)
#         self.assertEquals(sess.publish_date, publish)
#         self.assertEquals(sess.expire_date, expire)
#         self.assertEquals(sess.start_date, start)
#         self.assertEquals(sess.end_date, end)
#         self.assertEquals(sess.prev_session.expire_date, sess.publish_date)
#         self.assertLess(sess.prev_session.end_date, sess.start_date)
#         self.assertEquals(sess.prev_session.end_date, prev_end)


# end class SessionDateTests

# end of test.py file

from django.test import TestCase
from .models import Location, Session  # , Subject, ClassOffer, Profile, Registration, Payment
from datetime import date, timedelta

# Create your tests here.


class SessionModelTests(TestCase):

    def test_compute_end_date(self):
        """ The end date should be when the last class of this session is held.
            First, this depends on what is the latest a class could start:
            If max_day_shift is negative or 0, then start on key_day_date.
            If it is positive, then we start that many days after key_date.
            Therefore, the end_date will be duration number of weeks after this latest starting class.
        """
        now = date.today()
        key_day = now - timedelta(days=1)
        day_adjust = 0
        duration = 5
        publish = key_day - timedelta(days=7*(duration - 1))
        expire = key_day + timedelta(days=8)
        last_class = key_day + timedelta(days=7*duration)
        last_class = last_class + timedelta(days=day_adjust) if day_adjust > 0 else last_class
        test_sess = Session(
            name='test_session',
            key_day_date=key_day,
            max_day_shift=day_adjust,
            num_weeks=duration,
            publish_date=publish,
            expire_date=expire,
            )
        self.assertEquals(test_sess.end_date, last_class)
# end class SessionModelTests


# end of test.py file

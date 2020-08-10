from django.test import TransactionTestCase, TestCase
from .helper_views import decide_session, Session
from datetime import date, timedelta


class NewSiteDecideSession(TestCase):
    """ No initial data in the database. """

    def test_new_site_no_sessions(self):
        """ Before the admin has put any Sessions in, the site and app should not break """
        result = decide_session()
        self.assertEqual(len(result), 0)

    def test_raise_error_if_double_filter(self):
        """ Should raise an error if trying to filter by both session name and display date. """
        kwargs = {'sess': 'some_name', 'display_date': date.today()}
        with self.assertRaises(SyntaxError):
            decide_session(**kwargs)


class CurrentSessionSelection(TransactionTestCase):
    """ Critical views of current classes and content depend on the decide_session function. """
    fixtures = ['tests/fixtures/db_basic.json', 'tests/fixtures/db_hidden.json']
    # Should have a January_2020 session that has expired

    def test_only_current_published_session(self):
        """ Returns only currently published session, and no expired sessions """
        now = date.today()
        publish_date = now - timedelta(days=7*3)
        expire_date = now + timedelta(days=7*1)
        sess = Session.objects.create(name='test', key_day_date=now, publish_date=publish_date, expire_date=expire_date)
        result = decide_session()

        self.assertIn(sess, result)
        self.assertTrue(len(result) == 1)
        self.assertGreater(result[0].expire_date, now)

    def test_does_not_show_sessions_not_yet_published(self):
        """ Doesn't show future unpublished sessions """
        now = date.today()
        start = now + timedelta(days=7*5)
        publish_date = now + timedelta(days=7*2)
        expire_date = start + timedelta(days=7*2)
        sess = Session.objects.create(name='t1', key_day_date=start, publish_date=publish_date, expire_date=expire_date)
        result = decide_session()

        self.assertNotIn(sess, result)
        self.assertTrue(len(result) > 0)
        self.assertLess(result[0].publish_date, now)

    def test_all_sessions_expired(self):
        """ If all Sessions have expired, it should return the last expired session """
        now = date.today()
        initial = Session.objects.first()
        sess = Session.objects.create(name='june')
        result = decide_session()

        self.assertIsNotNone(initial)
        self.assertGreater(now, sess.expire_date)
        self.assertIn(sess, result)
        self.assertTrue(len(result) == 1)

    def test_requested_date(self):
        """ The decide_session has a 'display_date' parameter to view sessions live on that date. """
        initial = Session.objects.first()
        test_date = initial.publish_date + timedelta(days=2)
        result = decide_session(display_date=test_date)

        self.assertGreater(test_date, initial.publish_date)
        self.assertLess(test_date, initial.expire_date)
        self.assertIn(initial, result)

    def test_returns_many_published_session(self):
        """ When there are multiple, return all of the sessions published for a given date. """
        initial = Session.objects.first()
        publish = initial.publish_date + timedelta(days=1)
        expire = initial.expire_date + timedelta(days=1)
        key_day = initial.key_day_date + timedelta(days=1)
        overlap = Session.objects.create(name='overlap', key_day_date=key_day, publish_date=publish, expire_date=expire)
        test_date = publish + timedelta(days=1)
        result = decide_session(display_date=test_date)

        self.assertGreater(test_date, publish)
        self.assertLess(test_date, expire)
        self.assertGreater(test_date, initial.publish_date)
        self.assertLess(test_date, initial.expire_date)
        self.assertIn(initial, result)
        self.assertIn(overlap, result)

    def test_requested_session_name(self):
        """ The decide_session has a 'sess' parameter that accepts a session name """
        initial = Session.objects.first()
        name = initial.name
        result = decide_session(sess=name)

        self.assertIn(initial, result)
        self.assertTrue(len(result) == 1)

    def test_requested_session_name_not_existing(self):
        """ Should be an empty list if there was no session matching given name(s) """
        name = 'fake_1998'
        empty = Session.objects.filter(name__in=[name]).first()
        result = decide_session(sess=name)
        self.assertEqual(len(result), 0)
        self.assertIsNone(empty)

    def test_requested_all_sessions(self):
        """ If the 'sess' parameter is set to 'all', then return all the sessions. """
        sess = Session.objects.create(name='defaults')
        all_sess = Session.objects.all()
        result = decide_session(sess='all')

        self.assertIn(sess, result)
        self.assertTrue(len(all_sess) > 1)
        self.assertTrue(len(result) > 1)
        self.assertCountEqual(all_sess, result)

    def test_requested_multiple_session_names(self):
        """ The 'sess' parameter can be a list of session names, return all of them """
        initial = Session.objects.first()
        names = ['defaults']
        sess = Session.objects.create(name=names[0])
        names.append(initial.name)
        result = decide_session(sess=names)

        self.assertIn(initial, result)
        self.assertIn(sess, result)
        self.assertTrue(len(result) == 2)


# end test_decide_session file

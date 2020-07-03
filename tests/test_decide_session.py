from django.test import TransactionTestCase  # , TestCase
from django.db.models.query import QuerySet
from classwork.views import decide_session
from classwork.models import Session
from datetime import date, timedelta


class CurrentSessionSelection(TransactionTestCase):
    """ Critical views of current classes and content depend on the decide_session function. """
    fixtures = ['tests/db_basic.json']  # Has a May_2020 session that has expired

    def test_new_site_no_sessions(self):
        """ Before the admin has put any Sessions in, the site and app should not break """
        pass

    def test_only_current_published_session(self):
        """ Returns only currently published session, and no expired sessions """
        now = date.today()
        publish_date = now - timedelta(days=7*3)
        expire_date = now + timedelta(days=7*1)
        sess = Session.objects.create(name='test', key_day_date=now, publish_date=publish_date, expire_date=expire_date)
        result = decide_session()
        if isinstance(result, QuerySet):
            result = list(result)

        self.assertIn(sess, result)
        self.assertTrue(len(result) == 1)
        self.assertGreater(result[0].expire_date, now)

    def test_does_not_show_not_yet_published_session(self):
        """ Doesn't show future unpublished sessions """
        pass

    def test_current_many_published_session(self):
        """ Returns all of the sessions currently published if there are multiple """
        pass

    def test_all_sessions_expired(self):
        """ If all Sessions have expired, it should return the last expired session """
        pass

    def test_requested_date(self):
        """ The decide_session has a 'display_date' parameter to view sessions live on that date. """
        pass

    def test_requested_session_name(self):
        """ The decide_session has a 'sess' parameter that accepts a session name """
        pass

    def test_requested_session_name_not_existing(self):
        """ Should be an empty list if there was no session matching given name(s) """
        pass

    def test_requested_all_sessions(self):
        """ If the 'sess' parameter is set to 'all', then return all the sessions. """
        pass

    def test_requested_multiple_session_names(self):
        """ The 'sess' parameter can be a list of session names, return all of them """
        pass


# end test_decide_session file

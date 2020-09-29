from django.test import TestCase  # , Client, TransactionTestCase, RequestFactory,
# from django.urls import reverse
from unittest import skip
from django.utils.module_loading import import_string
from .helper_views import MimicAsView, decide_session, ClassOffer
# , Session, Subject, Staff, Student, Resource, UserHC, AnonymousUser, USER_DEFAULTS, OTHER_USER,
# @skip("Not Implemented")


class ClassOfferListViewTests(MimicAsView, TestCase):
    url_name = 'classoffer_list'
    viewClass = ClassOfferListView = import_string('classwork.views.ClassOfferListView')
    display_session_url_name = 'classoffer_display_session'
    display_date_url_name = 'classoffer_display_date'
    query_order_by = viewClass.query_order_by

    def setUp(self):
        self.classoffers = self.setup_three_sessions()
        self.view = self.setup_view('get')

    def test_get_queryset(self, display_session=None, display_date=None):
        """Expect to only contain the Sessions returned by decide_session as requested (or default). """
        display_session = display_session or self.view.kwargs.get('display_session', None)
        display_date = display_date or self.view.kwargs.get('display_date', None)
        self.view.kwargs['display_session'] = display_session
        self.view.kwargs['display_date'] = display_date
        view_queryset = self.view.get_queryset()
        is_ordered = getattr(view_queryset, 'ordered', False)
        transform = repr
        sessions = decide_session(sess=display_session, display_date=display_date)
        model_query = ClassOffer.objects.filter(session__in=sessions)
        if is_ordered:
            order = getattr(self, 'query_order_by', [])
            model_query = model_query.order_by(*order) if order else model_query
        model_list = [transform(ea) for ea in model_query.all()]
        expected_list = [transform(ea) for ea in self.classoffers['curr_sess']]

        self.assertQuerysetEqual(view_queryset, expected_list, transform=transform, ordered=False)
        self.assertQuerysetEqual(view_queryset, model_list, transform=transform, ordered=False)  # TODO: is_ordered
        self.assertSetEqual(set(expected_list), set(model_list))
        self.assertSetEqual(set(transform(ea) for ea in view_queryset.all()), set(model_list))

    def test_get_context_data(self, display_session=None, display_date=None):
        display_session = display_session or self.view.kwargs.get('display_session', None)
        display_date = display_date or self.view.kwargs.get('display_date', None)
        self.view.kwargs['display_session'] = display_session
        self.view.kwargs['display_date'] = display_date
        sessions = decide_session(sess=display_session, display_date=display_date)
        context_sessions = ', '.join([ea.name for ea in sessions])
        expected_subset = {'sessions': context_sessions}
        display_session_subset = {'display_session': display_session}
        display_date_subset = {'display_date': display_date}
        actual = self.view.get_context_data()

        self.assertDictContainsSubset(expected_subset, actual)
        self.assertDictContainsSubset(display_session_subset, actual)
        self.assertDictContainsSubset(display_date_subset, actual)


class CheckinListViewTests(MimicAsView, TestCase):
    """Using MimicAsView, with three sessions and the viewClass created with a GET request. """
    url_name = 'checkin'
    viewClass = import_string('classwork.views.Checkin')
    query_order_by = viewClass.query_order_by

    def setUp(self):
        self.classoffers = self.setup_three_sessions()
        self.view = self.setup_view('get')

    def test_get_queryset(self, display_session=None, display_date=None):
        display_session = display_session or self.view.kwargs.get('display_session', None)
        display_date = display_date or self.view.kwargs.get('display_date', None)
        self.view.kwargs['display_session'] = display_session
        self.view.kwargs['display_date'] = display_date
        view_queryset = self.view.get_queryset()
        is_ordered = getattr(view_queryset, 'ordered', False)
        transform = repr
        sessions = decide_session(sess=display_session, display_date=display_date)
        model_query = ClassOffer.objects.filter(session__in=sessions)
        if is_ordered:
            order = getattr(self, 'query_order_by', [])
            model_query = model_query.order_by(*order) if order else model_query
        model_list = [transform(ea) for ea in model_query.all()]
        expected_list = [transform(ea) for ea in self.classoffers['curr_sess']]

        self.assertQuerysetEqual(view_queryset, expected_list, transform=transform, ordered=False)
        self.assertQuerysetEqual(view_queryset, model_list, transform=transform, ordered=False)  # TODO: is_ordered
        self.assertSetEqual(set(expected_list), set(model_list))
        self.assertSetEqual(set(transform(ea) for ea in view_queryset.all()), set(model_list))

    def test_get_context_data(self, display_session=None, display_date=None):
        display_session = display_session or self.view.kwargs.get('display_session', None)
        display_date = display_date or self.view.kwargs.get('display_date', None)
        self.view.kwargs['display_session'] = display_session
        self.view.kwargs['display_date'] = display_date
        self.view.object_list = self.view.get_queryset()  # This step normally done in self.view.get()
        sessions = decide_session(sess=display_session, display_date=display_date)
        context_sessions = ', '.join([ea.name for ea in sessions])
        expected_subset = {'sessions': context_sessions}
        display_session_subset = {'display_session': display_session}  # likely None, unless visited prev or next.
        display_date_subset = {'display_date': display_date}  # likely None, unless a feature uses this date feature.
        actual = self.view.get_context_data()

        self.assertDictContainsSubset(expected_subset, actual)
        self.assertDictContainsSubset(display_session_subset, actual)
        self.assertDictContainsSubset(display_date_subset, actual)

    def test_get_context_data_with_display_session_value(self, display_date=None):
        display_session = [getattr(co_list[0].session, 'name', '') for sess_name, co_list in self.classoffers.items()]
        display_session = ','.join(display_session)
        display_date = display_date or self.view.kwargs.get('display_date', None)
        self.test_get_context_data(display_session=display_session, display_date=display_date)

    def test_get_context_data_with_display_date_value(self, display_session=None):
        """Check that we still get a result even if all Sessions have expired. """
        from datetime import timedelta
        display_session = display_session or self.view.kwargs.get('display_session', None)
        last_sess_co = self.classoffers['new_sess']
        last_sess = getattr(last_sess_co[0], 'session', None)
        display_date = str(last_sess.expire_date + timedelta(days=2))
        self.test_get_context_data(display_session=display_session, display_date=display_date)


@skip("Not Implemented Feature")
class SubjectProgressListViewTests(MimicAsView, TestCase):
    url_name = ''  # None created yet in classwork.urls
    viewClass = SubjectProgressView = import_string('classwork.views.SubjectProgressView')


@skip("Not Implemented")
class ClassOfferDetailViewTests(MimicAsView, TestCase):
    url_name = 'classoffer_detail'
    viewClass = ClassOfferDetailView = import_string('classwork.views.ClassOfferDetailView')


# end test_instruction_views.py

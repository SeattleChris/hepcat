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
        """ Expect to only contain the Sessions returned by decide_session as requested (or default). """
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
        self.assertQuerysetEqual(view_queryset, model_list, transform=transform, ordered=is_ordered)
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
        display_session_subset = {'display_session': None}
        display_date_subset = {'display_date': None}
        actual = self.view.get_context_data()

        self.assertDictContainsSubset(expected_subset, actual)
        self.assertDictContainsSubset(display_session_subset, actual)
        self.assertDictContainsSubset(display_date_subset, actual)


@skip("Not Implemented")
class CheckinListViewTests(MimicAsView, TestCase):
    url_name = 'checkin'
    viewClass = import_string('classwork.views.Checkin')

    def setUp(self):
        self.classoffers = self.setup_three_sessions()
        self.view = self.setup_view('get')

    @skip("Not Implemented")
    def test_get_queryset(self):
        pass

    @skip("Not Implemented")
    def test_get_context_data(self):
        pass


@skip("Not Implemented Feature")
class SubjectProgressListViewTests(MimicAsView, TestCase):
    url_name = ''  # None created yet in classwork.urls
    viewClass = SubjectProgressView = import_string('classwork.views.SubjectProgressView')


@skip("Not Implemented")
class ClassOfferDetailViewTests(MimicAsView, TestCase):
    url_name = 'classoffer_detail'
    viewClass = ClassOfferDetailView = import_string('classwork.views.ClassOfferDetailView')


# end test_instruction_views.py

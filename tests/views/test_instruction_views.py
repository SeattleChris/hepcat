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
    query_order_by = ('session__key_day_date', '_num_level', )

    def setUp(self):
        self.classoffers = self.setup_three_sessions()
        self.view = self.setup_view('get')

    def test_get_queryset(self):
        """ Expect to only contain the Sessions returned by decide_session as requested (or default). """
        view_queryset = self.view.get_queryset()
        is_ordered = getattr(view_queryset, 'ordered', False)
        transform = repr
        sessions = decide_session()
        model_query = ClassOffer.objects.filter(session__in=sessions)
        found_query = model_query
        if is_ordered:
            order = getattr(self, 'query_order_by', [])
            model_query = model_query.order_by(*order) if order else model_query
        model_list = [transform(ea) for ea in model_query.all()]
        expected_list = [transform(ea) for ea in self.classoffers['curr_sess']]

        self.assertQuerysetEqual(found_query, expected_list, transform=transform, ordered=False)
        self.assertQuerysetEqual(view_queryset, expected_list, transform=transform, ordered=False)
        self.assertSetEqual(set(expected_list), set(model_list))
        self.assertSetEqual(set(transform(ea) for ea in view_queryset.all()), set(model_list))
        # self.assertQuerysetEqual(view_queryset, model_list, transform=transform, ordered=is_ordered)

    def test_get_context_data(self):
        sessions = decide_session()
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

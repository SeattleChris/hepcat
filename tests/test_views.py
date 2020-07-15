from django.test import TestCase  # , TransactionTestCase
# from unittest import skip
# from .helper import SimpleModelTests
from classwork.views import AboutUsListView  # , SubjectProgressView, ClassOfferDetailView, ClassOfferListView, Checkin
from classwork.models import Profile, SiteContent
from users.models import UserHC
# from classwork.models import Location, Resource, SiteContent, Subject, ClassOffer, Profile
# from classwork.models import Session, Payment, Registration, Notify
# from datetime import date, timedelta
# @skip("Not Implemented")


class AboutUsListTests(TestCase):

    def test_queryset_is_only_staff(self):
        staff_user = UserHC.create_user()
        staff = Profile.objects.filter(user__is_staff=True).all()
        view = AboutUsListView()

        self.assertQuerysetEqual(staff, view.get_queryset())

    def test_get_context_data(self):
        print('================================ NEW TEST IS HERE =====================================')
        target_name = 'business_about'
        test_text = 'This is the about text we added. '
        initial_about = SiteContent.objects.filter(name=target_name).first()
        initial_about = initial_about.text if initial_about else ''
        view = AboutUsListView()
        initial_context = view.get_context_data()
        about = SiteContent.objects.create(name=target_name, text=test_text)
        about.save()
        # about.from_db
        later_context = view.get_context_data()

        self.assertEqual(initial_context[target_name] == initial_about)
        self.assertEqual(later_context[target_name] == about.text)


# end test_views.py

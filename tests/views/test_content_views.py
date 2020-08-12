from django.test import Client, TestCase  # , TransactionTestCase, RequestFactory,
from django.urls import reverse
from unittest import skip
from django.utils.module_loading import import_string
from .helper_views import MimicAsView, Staff, Student, SiteContent, Resource  # , decide_session,
from .helper_views import UserHC, AnonymousUser, USER_DEFAULTS, OTHER_USER  # , ClassOffer, Session, Subject,
# @skip("Not Implemented")


class AboutUsListTests(TestCase):
    url_name = 'aboutus'
    viewClass = import_string('classwork.views.AboutUsListView')
    ProfileStaff_query = Staff.objects  # Profile.objects.filter(is_staff=True) if single Profile model.
    ProfileStudent_query = Student.objects  # Profile.objects.filter(is_student=True) if single Profile model.
    view = viewClass()

    def get_staff_list(self, transform, is_ordered):
        """ Used to get the transformed list of expected staff users. """
        staff_query = self.ProfileStaff_query.filter(user__is_active=True)
        if is_ordered:
            order = getattr(self, 'query_order_by', [])
            staff_query = staff_query.order_by(*order) if order else staff_query
        return [transform(ea) for ea in staff_query.all()]

    def test_queryset_has_active_admin(self):
        """ The queryset should have currently active admin staff members. """
        kwargs = USER_DEFAULTS.copy()
        kwargs['is_admin'] = True
        user = UserHC.objects.create_user(**kwargs)
        user.save()
        staff = getattr(user, 'staff', None)
        view_queryset = self.view.get_queryset()
        is_ordered = getattr(view_queryset, 'ordered', False)
        transform = repr
        all_staff_list = self.get_staff_list(transform, is_ordered)

        self.assertTrue(user.is_staff)
        self.assertQuerysetEqual(view_queryset, all_staff_list, transform=transform, ordered=is_ordered)
        self.assertIsNotNone(staff)
        self.assertIn(staff, list(view_queryset.all()))

    def test_queryset_has_active_teachers(self):
        """ The queryset should have currently active teacher staff members. """
        kwargs = USER_DEFAULTS.copy()
        kwargs['is_teacher'] = True
        user = UserHC.objects.create_user(**kwargs)
        user.save()
        staff = getattr(user, 'staff', None)
        view_queryset = self.view.get_queryset()
        is_ordered = getattr(view_queryset, 'ordered', False)
        transform = repr
        all_staff_list = self.get_staff_list(transform, is_ordered)

        self.assertTrue(user.is_staff)
        self.assertQuerysetEqual(view_queryset, all_staff_list, transform=transform, ordered=is_ordered)
        self.assertIsNotNone(staff)
        self.assertIn(staff, list(view_queryset.all()))

    def test_queryset_not_have_inactive_staff(self):
        """ The queryset should not have inactive staff users. """
        kwargs = USER_DEFAULTS.copy()
        kwargs['is_teacher'] = True
        kwargs['is_active'] = False
        user = UserHC.objects.create_user(**kwargs)
        user.save()
        staff = getattr(user, 'staff', None)
        view_queryset = self.view.get_queryset()
        is_ordered = getattr(view_queryset, 'ordered', False)
        transform = repr
        all_staff_list = self.get_staff_list(transform, is_ordered)

        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_active)
        self.assertQuerysetEqual(view_queryset, all_staff_list, transform=transform, ordered=is_ordered)
        self.assertIsNotNone(staff)
        self.assertNotIn(staff, list(view_queryset.all()))
        self.assertIn(staff, self.ProfileStaff_query.filter(user__is_active=False))

    def test_queryset_not_have_students(self):
        """ The queryset should not have student only users. """
        kwargs = USER_DEFAULTS.copy()
        kwargs['is_admin'] = False
        kwargs['is_student'] = True
        user = UserHC.objects.create_user(**kwargs)
        user.save()
        staff = getattr(user, 'staff', None)
        student = getattr(user, 'student', None)
        view_queryset = self.view.get_queryset()
        is_ordered = getattr(view_queryset, 'ordered', False)
        transform = repr
        all_staff_list = self.get_staff_list(transform, is_ordered)
        users_from_view_qs = [getattr(ea, 'user', None) for ea in view_queryset.all()]
        student_query = self.ProfileStudent_query.filter(user__is_active=True)

        self.assertTrue(user.is_student)
        self.assertFalse(user.is_staff)
        self.assertQuerysetEqual(view_queryset, all_staff_list, transform=transform, ordered=is_ordered)
        self.assertIsNone(staff)
        self.assertNotIn(user, users_from_view_qs)
        self.assertIsNotNone(student)
        self.assertIn(student, list(student_query.all()))

    @skip("Not Implemented")
    def test_queryset_has_expected_profile_order(self):
        """ The queryset should have currently active staff members. """
        kwargs = USER_DEFAULTS.copy()
        kwargs['is_admin'] = True
        user = UserHC.objects.create_user(**kwargs)
        user.save()
        view_queryset = self.view.get_queryset()
        is_ordered = getattr(view_queryset, 'ordered', False)
        transform = repr
        all_staff_list = self.get_staff_list(transform, is_ordered)
        self.assertTrue(user.is_staff)
        self.assertQuerysetEqual(view_queryset, all_staff_list, transform=transform, ordered=is_ordered)

    def test_get_context_data(self):
        """ Testing site before and after having a 'business_about' SiteContent.  """
        target_name = 'business_about'
        test_text = 'This is the about text we added. '
        initial_about = SiteContent.objects.filter(name=target_name).first()
        initial_about = getattr(initial_about, 'text', '') if initial_about else ''
        c = Client()
        url = reverse(self.url_name)
        initial_response = c.get(url)
        about = SiteContent.objects.create(name=target_name, text=test_text)
        about.save()
        later_response = c.get(url)

        self.assertEqual(initial_response.status_code, 200)
        self.assertEqual(later_response.status_code, 200)
        self.assertNotContains(initial_response, test_text)
        self.assertContains(later_response, about.text)
        self.assertEqual(test_text, about.text)


class ProfileViewTests(MimicAsView, TestCase):
    url_name = 'profile_page'
    viewClass = ProfileView = import_string('classwork.views.ProfileView')
    user_url_name = 'profile_user'

    def setUp(self):
        self.view = self.setup_view('get')

    def test_get_object_superuser(self):
        kwargs = USER_DEFAULTS.copy()
        kwargs['username'] = None
        user = UserHC.objects.create_superuser(**kwargs)
        user.save()
        self.view.request.user = user
        actual = self.view.get_object()
        self.assertIsNotNone(getattr(user, 'staff', None))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_student)
        self.assertIsNotNone(getattr(user, 'student', None))
        self.assertEqual(user.staff, actual)

    def test_get_object_admin(self):
        kwargs = USER_DEFAULTS.copy()
        kwargs['is_admin'] = True
        user = UserHC.objects.create_user(**kwargs)
        user.save()
        self.view.request.user = user
        actual = self.view.get_object()
        self.assertIsNotNone(getattr(user, 'staff', None))
        self.assertTrue(user.is_staff)
        self.assertEqual(user.staff, actual)
        self.assertFalse(user.is_student)
        self.assertIsNone(getattr(user, 'student', None))

    def test_get_object_teacher(self):
        kwargs = USER_DEFAULTS.copy()
        kwargs['is_teacher'] = True
        user = UserHC.objects.create_user(**kwargs)
        user.save()
        self.view.request.user = user
        actual = self.view.get_object()
        self.assertIsNotNone(getattr(user, 'staff', None))
        self.assertTrue(user.is_staff)
        self.assertEqual(user.staff, actual)
        self.assertFalse(user.is_student)
        self.assertIsNone(getattr(user, 'student', None))

    def test_get_object_student(self):
        kwargs = USER_DEFAULTS.copy()
        kwargs['is_student'] = True
        user = UserHC.objects.create_user(**kwargs)
        user.save()
        self.view.request.user = user
        actual = self.view.get_object()
        self.assertTrue(user.is_student)
        self.assertIsNotNone(getattr(user, 'student', None))
        self.assertEqual(user.student, actual)
        self.assertIsNone(getattr(user, 'staff', None))
        self.assertFalse(user.is_staff)

    def test_get_object_student_teacher(self):
        kwargs = USER_DEFAULTS.copy()
        kwargs['is_student'] = True
        kwargs['is_teacher'] = True
        user = UserHC.objects.create_user(**kwargs)
        user.save()
        self.view.request.user = user
        actual = self.view.get_object()
        self.assertTrue(user.is_student)
        self.assertIsNotNone(getattr(user, 'student', None))
        self.assertIsNotNone(getattr(user, 'staff', None))
        self.assertTrue(user.is_staff)
        self.assertEqual(user.staff, actual)

    def test_get_object_anonymous(self):
        user = AnonymousUser
        self.view.request.user = user
        actual = self.view.get_object()

        self.assertFalse(user.is_staff)
        self.assertIsNone(getattr(user, 'staff', None))
        self.assertIsNone(getattr(user, 'is_student', None))
        self.assertIsNone(getattr(user, 'student', None))
        self.assertIsNone(actual)
        self.assertEqual(getattr(user, 'student', None), actual)

    def test_get_object_view_student_by_admin(self):
        kwargs = USER_DEFAULTS.copy()
        kwargs['is_admin'] = True
        user = UserHC.objects.create_user(**kwargs)
        user.save()
        other_kwargs = OTHER_USER.copy()
        other_kwargs['is_student'] = True
        other = UserHC.objects.create_user(**other_kwargs)
        other.save()
        self.view.request.user = user
        self.view.kwargs['id'] = other.id
        actual = self.view.get_object()
        self.assertIsNotNone(getattr(user, 'staff', None))
        self.assertTrue(user.is_staff)
        self.assertTrue(other.is_student)
        self.assertIsNotNone(getattr(other, 'student', None))
        self.assertEqual(other.student, actual)

    def test_not_permitted_view_other_shows_self(self):
        kwargs = USER_DEFAULTS.copy()
        kwargs['is_student'] = True
        user = UserHC.objects.create_user(**kwargs)
        user.save()
        other_kwargs = OTHER_USER.copy()
        other_kwargs['is_student'] = True
        other = UserHC.objects.create_user(**other_kwargs)
        other.save()
        self.view.request.user = user
        self.view.kwargs['id'] = other.id
        self.assertIsNotNone(getattr(user, 'student', None))
        self.assertTrue(user.is_student)
        self.assertFalse(user.is_staff)
        self.assertTrue(other.is_student)
        self.assertIsNotNone(getattr(other, 'student', None))
        actual = self.view.get_object()
        self.assertEqual(user.student, actual)

    def test_admin_view_not_existing_student_raise_error(self):
        kwargs = USER_DEFAULTS.copy()
        kwargs['is_admin'] = True
        user = UserHC.objects.create_user(**kwargs)
        user.save()
        self.view.request.user = user
        last_user = UserHC.objects.order_by('id').last()
        target_id = last_user.id + 1
        self.view.kwargs['id'] = target_id

        self.assertIsNotNone(getattr(user, 'staff', None))
        self.assertIsNone(UserHC.objects.filter(id=target_id).first())
        with self.assertRaises(UserHC.DoesNotExist):
            self.view.get_object()

    # @skip("Not Implemented")
    def test_get_context_data(self):
        classoffers = self.setup_three_sessions()
        kwargs = USER_DEFAULTS.copy()
        kwargs['is_student'] = True
        user = UserHC.objects.create_user(**kwargs)
        user.save()
        self.view.request.user = user
        self.view.object = self.view.get_object()  # This step normally done in self.view.get()
        taken_list = [arr[0] for sess, arr in classoffers.items()]
        first_subj = taken_list[0].subject
        first_res = Resource.objects.create(content_type='text', title="First Subject Resource")
        first_res.save()
        first_subj.resources.add(first_res)
        resources = [first_res]
        for ea in taken_list:
            res = Resource.objects.create(content_type='text', title=str(ea) + 'Res')
            res.save()
            ea.resources.add(res)
            resources.append(res)
        user.student.taken.add(*taken_list)
        expected_subset = {'had': taken_list, 'resources': {'text': resources}}
        actual_context = self.view.get_context_data(object=self.view.object)  # matches the typical call in get()
        self.assertDictContainsSubset(expected_subset, actual_context)

    @skip("Not Implemented")
    def test_visit_view(self):
        kwargs = USER_DEFAULTS.copy()
        kwargs['is_student'] = True
        user = UserHC.objects.create_user(**kwargs)
        user.save()
        self.view.request.user = user
        classoffers = self.setup_three_sessions()
        take_1 = classoffers['old_sess'][0]
        student = user.student
        student.taken.add(take_1)
        good_text = str(take_1)
        avoid = classoffers['old_sess'][1]
        bad_text = str(avoid)
        self.client_visit_view(good_text, bad_text)
        take_2 = classoffers['curr_sess'][1]
        student.taken.add(take_2)
        good_text_2 = str(take_2)
        self.client_visit_view(good_text_2)


@skip("Not Implemented")
class LocationListViewTests(MimicAsView, TestCase):
    url_name = 'location_list'
    viewClass = LocationListView = import_string('classwork.views.LocationListView')


@skip("Not Implemented")
class LocationDetailViewTests(MimicAsView, TestCase):
    url_name = 'location_detail'
    viewClass = LocationDetailView = import_string('classwork.views.LocationDetailView')


@skip("Not Implemented")
class ResourceDetailViewTests(MimicAsView, TestCase):
    url_name = 'location_list'
    viewClass = ResourceDetailView = import_string('classwork.views.ResourceDetailView')


# end test_content_views.py

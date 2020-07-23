from django.test import TestCase, TransactionTestCase
from django.conf import settings
from unittest import skip
from .helper import SimpleModelTests
from classwork.models import Location, Resource, SiteContent, Subject, ClassOffer, Profile
from classwork.models import Session, Payment, Registration, Notify
from users.models import UserHC
from datetime import date, time, timedelta, datetime as dt

# Create your tests here.


class SiteContentModelTests(SimpleModelTests, TestCase):
    Model = SiteContent
    repr_dict = {'SiteContent': 'name'}


class LocationModelTests(SimpleModelTests, TestCase):
    Model = Location
    repr_dict = {'Location': 'name', 'Link': 'map_link'}


class ResourceModelTests(SimpleModelTests, TransactionTestCase):
    fixtures = ['tests/fixtures/db_basic.json', 'tests/fixtures/db_hidden.json']
    Model = Resource
    repr_dict = {'Resource': 'related_type', 'Type': 'content_type'}
    str_list = ['title', 'related_type', 'content_type']

    # Setup for publish method
    # Need a student user & profile
    # ? Need a Location
    # Need a Session, Subject, and ClassOffer
    # The student needs to be associated with the ClassOffer
    # Need Resource(s) attached to a Subject or ClassOffer
    # - Can't view before joining
    # - Immediately available once joined
    # - Not yet published
    # - Already expired
    # # # #
    # Have
    # resource = Resource.objects.get(id=1) has .title = "Congrats on Finishing class!"
    # resource is connected to a Subject with id=1 and a ClassOffer with id=1
    # classoffer = ClassOffer.objects.get(id=1) is connected to resource and a Session, Subject, Location.
    # there is a student with id=1, and they have a registration for this classoffer.

    @skip("Not Implemented")
    def test_publish_not_view_if_not_joined(self):
        """ For a User NOT signed in a ClassOffer, determine they are NOT allowed to see an associated Resource. """
        student = Profile.objects.get(id=1)
        classoffer = ClassOffer.objects.get(id=1)
        # classoffer settings - 'key_day_date': '2020-04-30', 'num_weeks': 5 ==> class ended already.
        resource = Resource.objects.get(id=1)
        # resource has fields - user_type: 1 (student), avail: 200 (after finished), expire: 0 (never)
        available = resource.publish(classoffer)

        self.assertGreater(len(student.taken), 0)
        self.assertIn(classoffer, student.taken)
        self.assertIn(student, classoffer.students)
        self.assertEquals(resource.classoffer, classoffer)
        self.assertIn(resource, classoffer.resource_set)
        self.assertFalse(available)

    @skip("Not Implemented")
    def test_publish_can_view_avail_is_immediate(self):
        """ For a User signed in a ClassOffer, determine they are allowed to see an associated immediate Resource. """
        pass

    @skip("Not Implemented")
    def test_publish_can_view_during_published(self):
        """ For a User signed in a ClassOffer, determine they are allowed to see a currently published Resource. """
        pass

    @skip("Not Implemented")
    def test_publish_can_view_never_expired(self):
        """ For a User signed in a ClassOffer, determine they can view an associated never expired Resource. """
        print("=========================== ResourceModelTests - Running Here ========================================")
        student = Profile.objects.get(user=1)
        classoffer = ClassOffer.objects.get(id=1)
        # classoffer settings - 'key_day_date': '2020-04-30', 'num_weeks': 5 ==> class ended already.
        resource = Resource.objects.get(id=1)
        # resource has fields - user_type: 1 (student), avail: 200 (after finished), expire: 0 (never)
        available = resource.publish(classoffer)

        self.assertGreater(len(student.taken), 0)
        self.assertIn(classoffer, student.taken)
        self.assertEquals(resource.classoffer, classoffer)
        self.assertIn(student, classoffer.students)
        self.assertIn(resource, classoffer.resource_set)
        self.assertTrue(available)

    @skip("Not Implemented")
    def test_publish_not_view_before_publish(self):
        """ For a User signed in a ClassOffer, determine they do NOT see an associated Resource early. """
        pass

    @skip("Not Implemented")
    def test_publish_not_view_after_expired(self):
        """ For a User signed in a ClassOffer, they do NOT see an associated expired Resource. """
        pass


class SubjectModelTests(SimpleModelTests, TestCase):
    Model = Subject
    repr_dict = {'Subject': 'title', 'Level': 'level', 'Version': 'version'}
    str_list = ['_str_slug']


class ClassOfferModelTests(SimpleModelTests, TransactionTestCase):
    fixtures = ['tests/fixtures/db_basic.json', 'tests/fixtures/db_hidden.json']
    Model = ClassOffer
    repr_dict = {'Class Id': 'id', 'Subject': 'subject', 'Session': 'session'}
    str_list = ['subject', 'session']
    defaults = {}

    def test_full_price(self):
        subject = Subject.objects.first()
        classoffer = ClassOffer.objects.first()
        full_price = subject.full_price

        self.assertEqual(classoffer.subject_id, subject.id)
        self.assertEquals(full_price, classoffer.full_price)

    def test_pre_discount(self):
        subject = Subject.objects.first()
        classoffer = ClassOffer.objects.first()
        pre_discount = subject.pre_pay_discount

        self.assertEqual(classoffer.subject_id, subject.id)
        self.assertEquals(pre_discount, classoffer.pre_discount)

    def test_multi_discount_reports_discount(self):
        subject = Subject.objects.first()
        classoffer = ClassOffer.objects.first()
        multi_discount = subject.multiple_purchase_discount

        self.assertEqual(classoffer.subject_id, subject.id)
        self.assertTrue(subject.qualifies_as_multi_class_discount)
        self.assertEquals(multi_discount, classoffer.multi_discount)

    def test_multi_discount_not_qualified(self):
        subject = Subject.objects.first()
        subject.qualifies_as_multi_class_discount = False
        subject.save()
        classoffer = ClassOffer.objects.first()

        self.assertEquals(classoffer.subject_id, subject.id)
        self.assertFalse(subject.qualifies_as_multi_class_discount)
        self.assertGreater(subject.multiple_purchase_discount, 0)
        self.assertEquals(classoffer.multi_discount, 0)

    def test_multi_discount_zero_discount(self):
        subject = Subject.objects.first()
        subject.multiple_purchase_discount = 0
        subject.save()
        classoffer = ClassOffer.objects.first()

        self.assertEquals(classoffer.subject_id, subject.id)
        self.assertTrue(subject.qualifies_as_multi_class_discount)
        self.assertEquals(subject.multiple_purchase_discount, 0)
        self.assertEquals(classoffer.multi_discount, 0)

    def test_pre_price(self):
        classoffer = ClassOffer.objects.first()
        self_computed = classoffer.full_price - classoffer.pre_discount
        subject = Subject.objects.first()
        subj_computed = subject.full_price - subject.pre_pay_discount

        self.assertEqual(self_computed, classoffer.pre_price)
        self.assertEqual(classoffer.subject, subject)
        self.assertEqual(subj_computed, classoffer.pre_price)

    def test_skip_week_explain(self):
        classoffer = ClassOffer.objects.first()
        expected_string = f"but you still get {classoffer.session.num_weeks} class days"
        self.assertEqual(expected_string, classoffer.skip_week_explain)

    def test_end_time(self):
        model = ClassOffer.objects.first()
        now = dt.now()
        start = dt(now.year, now.month, now.day, model.start_time.hour, model.start_time.minute)
        end = start + timedelta(minutes=model.subject.num_minutes)

        self.assertEqual(end.time(), model.end_time)

    def test_day_singular(self):
        model = ClassOffer.objects.first()
        subject = Subject.objects.first()
        subject.num_weeks = 1
        subject.save()
        day = ClassOffer.DOW_CHOICES[model.class_day][1]

        self.assertEqual(model.subject, subject)
        self.assertFalse(model.subject.num_weeks > 1)
        self.assertEquals(model.day, day)

    def test_day_plural(self):
        model = ClassOffer.objects.first()
        day = ClassOffer.DOW_CHOICES[model.class_day][1]
        day = str(day) + 's'

        self.assertTrue(model.subject.num_weeks > 1)
        self.assertEquals(model.day, day)

    def test_day_short_singular(self):
        model = ClassOffer.objects.first()
        subject = Subject.objects.first()
        subject.num_weeks = 1
        subject.save()
        day = ClassOffer.DOW_CHOICES[model.class_day][1]
        day = day[:3]

        self.assertEqual(model.subject, subject)
        self.assertFalse(model.subject.num_weeks > 1)
        self.assertEquals(model.day_short, day)

    def test_day_short_plural(self):
        model = ClassOffer.objects.first()
        day = ClassOffer.DOW_CHOICES[model.class_day][1]
        day = day[:3]
        day += '(s)'

        self.assertTrue(model.subject.num_weeks > 1)
        self.assertEquals(model.day_short, day)

    def test_start_date_is_key_day(self):
        model = ClassOffer.objects.first()
        key_day = model.session.key_day_date
        key_day_of_week = key_day.weekday()
        if model.class_day != key_day_of_week:
            model.class_day = key_day_of_week
            model.save()

        self.assertEquals(model.class_day, key_day_of_week)
        self.assertEquals(model.start_date, model.session.key_day_date)

    def test_start_date_zero_max_shift(self):
        model = ClassOffer.objects.first()
        session = Session.objects.first()  # expected to be connected to model
        session.max_day_shift = 0
        session.save()
        key_day_of_week = session.key_day_date.weekday()
        if model.class_day != key_day_of_week:
            model.class_day = key_day_of_week
            model.save()

        self.assertEquals(model.session, session)
        self.assertEquals(session.max_day_shift, 0)
        self.assertEquals(model.class_day, key_day_of_week)
        self.assertEquals(model.start_date, session.key_day_date)

    def test_start_date_negative_shift(self):
        model = ClassOffer.objects.first()
        session = Session.objects.first()  # expected to be connected to model
        if session.max_day_shift >= 0:
            session.max_day_shift = -2
            session.save()
        key_day_of_week = session.key_day_date.weekday()
        if model.class_day == key_day_of_week:
            model.class_day += -1 if key_day_of_week > 0 else 6
            model.save()
        actual_date_shift = model.class_day - key_day_of_week
        if actual_date_shift > 0:
            actual_date_shift -= 7
        result_date = session.key_day_date + timedelta(days=actual_date_shift)

        self.assertEquals(model.session, session)
        self.assertLess(session.max_day_shift, 0)
        self.assertNotEquals(model.class_day, key_day_of_week)
        self.assertNotEquals(actual_date_shift, 0)
        self.assertEquals(model.start_date, result_date)

    def test_start_date_positive_shift(self):
        model = ClassOffer.objects.first()
        session = Session.objects.first()  # expected to be connected to model
        if session.max_day_shift <= 0:
            session.max_day_shift = 2
            session.save()
        key_day_of_week = session.key_day_date.weekday()
        if model.class_day == key_day_of_week:
            model.class_day += 1 if key_day_of_week < 6 else -6
            model.save()
        actual_date_shift = model.class_day - key_day_of_week
        if actual_date_shift < 0:
            actual_date_shift += 7
        result_date = session.key_day_date + timedelta(days=actual_date_shift)

        self.assertEquals(model.session, session)
        self.assertGreater(session.max_day_shift, 0)
        self.assertNotEquals(model.class_day, key_day_of_week)
        self.assertNotEquals(actual_date_shift, 0)
        self.assertEquals(model.start_date, result_date)

    def test_start_date_out_of_negative_shift_range_opposite_direction(self):
        model = ClassOffer.objects.first()
        session = Session.objects.first()  # expected to be connected to model
        if session.max_day_shift >= 0 or session.max_day_shift == -6:
            session.max_day_shift = -2
            session.save()
        key_day_of_week = session.key_day_date.weekday()
        shift = 1
        result_date = session.key_day_date + timedelta(days=shift)
        target = key_day_of_week + shift
        if target > 6:
            target -= 7
        model.class_day = target
        model.save()

        self.assertEquals(model.session, session)
        self.assertLess(session.max_day_shift, 0)
        self.assertNotEquals(model.class_day, key_day_of_week)
        self.assertEquals(model.start_date, result_date)

    def test_start_date_out_of_positive_shift_range_opposite_direction(self):
        model = ClassOffer.objects.first()
        session = Session.objects.first()  # expected to be connected to model
        if session.max_day_shift <= 0 or session.max_day_shift == 6:
            session.max_day_shift = 2
            session.save()
        key_day_of_week = session.key_day_date.weekday()
        shift = -1
        result_date = session.key_day_date + timedelta(days=shift)
        target_day = key_day_of_week + shift
        if target_day < 0:
            target_day += 7
        model.class_day = target_day
        model.save()

        self.assertEquals(model.session, session)
        self.assertGreater(session.max_day_shift, 0)
        self.assertNotEquals(model.class_day, key_day_of_week)
        self.assertEquals(model.start_date, result_date)

    def test_start_date_beyond_negative_shift_range(self):
        model = ClassOffer.objects.first()
        session = Session.objects.first()  # expected to be connected to model
        if session.max_day_shift >= 0 or session.max_day_shift == -6:
            session.max_day_shift = -2
            session.save()
        key_day_of_week = session.key_day_date.weekday()
        shift = session.max_day_shift - 1
        result_date = session.key_day_date + timedelta(days=(shift + 7))
        target = key_day_of_week + shift
        if target < 0:
            target += 7
        model.class_day = target
        model.save()

        self.assertEquals(model.session, session)
        self.assertLess(session.max_day_shift, 0)
        self.assertNotEquals(model.class_day, key_day_of_week)
        self.assertEquals(model.start_date, result_date)

    def test_start_date_beyond_positive_shift_range(self):
        model = ClassOffer.objects.first()
        session = Session.objects.first()  # expected to be connected to model
        if session.max_day_shift <= 0 or session.max_day_shift == 6:
            session.max_day_shift = 2
            session.save()
        key_day_of_week = session.key_day_date.weekday()
        shift = session.max_day_shift + 1
        result_date = session.key_day_date + timedelta(days=(shift - 7))
        target = key_day_of_week + shift
        if target > 6:
            target -= 7
        model.class_day = target
        model.save()

        self.assertEquals(model.session, session)
        self.assertGreater(session.max_day_shift, 0)
        self.assertNotEquals(model.class_day, key_day_of_week)
        self.assertEquals(model.start_date, result_date)

    def test_end_date_no_skips(self):
        subject = Subject.objects.first()
        session = Session.objects.first()
        if session.skip_weeks > 0:
            session.skip_weeks = 0
            session.save()
        model = ClassOffer.objects.first()
        if model.skip_weeks > 0:
            model.skip_weeks = 0
            model.save()
        expected = model.start_date + timedelta(days=7*(subject.num_weeks - 1))

        self.assertEquals(model.subject, subject)
        self.assertEquals(model.session, session)
        self.assertEquals(session.skip_weeks, 0)
        self.assertEquals(model.skip_weeks, 0)
        self.assertEquals(model.end_date, expected)

    def test_end_date_skips_on_session_not_classoffer(self):
        subject = Subject.objects.first()
        session = Session.objects.first()
        if session.skip_weeks == 0:
            session.skip_weeks = 1
            session.save()
        model = ClassOffer.objects.first()
        if model.skip_weeks > 0:
            model.skip_weeks = 0
            model.save()
        expected = model.start_date + timedelta(days=7*(subject.num_weeks - 1))

        self.assertEquals(model.subject, subject)
        self.assertEquals(model.session, session)
        self.assertGreater(session.skip_weeks, 0)
        self.assertEquals(model.skip_weeks, 0)
        self.assertEquals(model.end_date, expected)

    def test_end_date_with_skips(self):
        subject = Subject.objects.first()
        session = Session.objects.first()
        if session.skip_weeks == 0:
            session.skip_weeks = 1
            session.save()
        model = ClassOffer.objects.first()
        if model.skip_weeks == 0:
            model.skip_weeks = 1
            model.save()
        expected = model.start_date + timedelta(days=7*(subject.num_weeks + model.skip_weeks - 1))

        self.assertEquals(model.subject, subject)
        self.assertEquals(model.session, session)
        self.assertGreater(session.skip_weeks, 0)
        self.assertGreater(model.skip_weeks, 0)
        self.assertEquals(model.end_date, expected)

    def test_num_level(self):
        model = ClassOffer.objects.first()
        expected = model._num_level
        self.assertEqual(expected, model.num_level)

    def test_set_num_level_subject_level_bad_value(self):
        level_dict = Subject.LEVEL_ORDER
        higher = 100 + max(level_dict.values())
        model = ClassOffer.objects.first()
        subject = Subject.objects.first()  # expected to be connected to model
        original = model.num_level
        subj_level, i = '', 0
        while subj_level in level_dict or subj_level == subject.level or level_dict.get(subj_level, '') == original:
            subj_level = Subject.LEVEL_CHOICES[i][0]
            i += 1
        subject.level = subj_level
        subject.save()
        expected = higher
        model.set_num_level()

        self.assertEquals(model.subject, subject)
        self.assertNotEqual(model.num_level, original)
        self.assertEquals(model.num_level, expected)

    def test_set_num_level_correct(self):
        level_dict = Subject.LEVEL_ORDER
        model = ClassOffer.objects.first()
        subject = Subject.objects.first()  # expected to be connected to model
        original = model.num_level
        subj_level, i = '', 0
        while subj_level not in level_dict or subj_level == subject.level or level_dict[subj_level] == original:
            subj_level = Subject.LEVEL_CHOICES[i][0]
            i += 1
        subject.level = subj_level
        subject.save()
        expected = level_dict.get(subj_level, None)
        model.set_num_level()

        self.assertEquals(model.subject, subject)
        self.assertNotEqual(model.num_level, original)
        self.assertEquals(model.num_level, expected)


class ProfileModelTests(SimpleModelTests, TestCase):
    Model = Profile
    repr_dict = {'Profile': 'full_name', 'User id': 'user_id'}
    str_list = ['full_name']
    defaults = {'email': 'fake@site.com', 'password': '1234', 'first_name': 'fa', 'last_name': 'fake'}

    def setUp(self):
        kwargs = self.defaults.copy()
        user = UserHC.objects.create_user(**kwargs)
        user.save()
        self.defaults = {}
        self.instance = user.profile  # triggers self.create_model to update this model instead of creating one.

    def test_taken_subject_is_related_subjects(self):
        model = self.instance
        versions = ('A', 'B', 'C', 'D', )
        subjs = []
        for level, string in Subject.LEVEL_CHOICES:
            subjs += [Subject.objects.create(level=level, version=ver, title=f"{level}_{ver}", ) for ver in versions]
        session = Session.objects.create(name='test_sess', key_day_date=date(2020, 1, 9))
        location = Location.objects.create(name='test_location', code='tl', address='12 main st', zipcode=98112, )
        kwargs = {'session': session, 'location': location, 'start_time': time(19, 0), }
        attended = [ClassOffer.objects.create(subject=subj, **kwargs) for subj in subjs]
        kwargs['session'] = Session.objects.create(name='test_sess2')  # Determines key_day_date based on previous
        attended += [ClassOffer.objects.create(subject=subj, **kwargs) for subj in subjs]
        model.taken.add(*attended)
        expected_subj_count = len(versions) * len(Subject.LEVEL_CHOICES)
        expected_classoffer_count = 2 * len(versions) * len(Subject.LEVEL_CHOICES)

        self.assertEqual(expected_classoffer_count, model.taken.count())
        self.assertEqual(expected_subj_count, len(model.taken_subjects))

    def test_highest_subject_correct_values(self):
        model = self.instance
        subj_has_level, i = '', -1
        while subj_has_level not in Subject.LEVEL_ORDER and subj_has_level is not None:
            i += 1
            subj_has_level = Subject.LEVEL_CHOICES[i][0] if i < len(Subject.LEVEL_CHOICES) else None
        if not subj_has_level:
            raise NotImplementedError("There must be at least one Subject.LEVEL_CHOICES in Subject.LEVEL_ORDER. ")
        expected_level_num = Subject.LEVEL_ORDER[subj_has_level]
        subj_no_level, i = '', -1
        while subj_no_level in Subject.LEVEL_ORDER or subj_no_level == '':
            i += 1
            subj_no_level = Subject.LEVEL_CHOICES[i][0] if i < len(Subject.LEVEL_CHOICES) else None
        levels = (subj_has_level, subj_no_level) if subj_no_level else (subj_has_level, )
        ver = Subject.VERSION_CHOICES[0][0]
        subjs = [Subject.objects.create(level=level, version=ver, title=f"{level}_{ver}", ) for level in levels]
        session = Session.objects.create(name='test_sess', key_day_date=date(2020, 1, 9))
        location = Location.objects.create(name='test_location', code='tl', address='12 main st', zipcode=98112, )
        kwargs = {'session': session, 'location': location, 'start_time': time(19, 0), }
        attended = [ClassOffer.objects.create(subject=subj, **kwargs) for subj in subjs]
        model.taken.add(*attended)
        result = model.highest_subject
        self.assertEqual(result['level_num__max'], expected_level_num)
        self.assertIn(subjs[0], result['subjects'])

    def test_highest_subject_no_values(self):
        model = self.instance
        result = model.highest_subject
        self.assertEqual(result['level_num__max'], None)
        self.assertEqual(result['subjects'].count(), 0)

    def test_level_methods_when_no_beg_attended(self):
        model = self.instance
        self.assertFalse(model.beg.get('done'))
        self.assertEqual(model.compute_level(), 0)

    def test_level_methods_when_only_some_beg_attended(self):
        model = self.instance
        level = Subject.LEVEL_CHOICES[0][0]
        beg_a_subj = Subject.objects.create(level=level, version='A', title='beg_a_test', )
        session = Session.objects.create(name='test_sess', key_day_date=date(2020, 1, 9))
        location = Location.objects.create(name='test_location', code='tl', address='12 main st', zipcode=98112, )
        kwargs = {'session': session, 'location': location, 'start_time': time(19, 0), }
        beg_a = ClassOffer.objects.create(subject=beg_a_subj, **kwargs)
        model.taken.add(beg_a)

        self.assertFalse(model.beg.get('done'))
        self.assertEqual(model.compute_level(), 1)

    def test_level_methods_when_beg_finished(self):
        model = self.instance
        level = Subject.LEVEL_CHOICES[0][0]
        versions = ('A', 'B', )
        subjs = [Subject.objects.create(level=level, version=ver, title=f"{level}_{ver}_test", ) for ver in versions]
        session = Session.objects.create(name='test_sess', key_day_date=date(2020, 1, 9))
        location = Location.objects.create(name='test_location', code='tl', address='12 main st', zipcode=98112, )
        kwargs = {'session': session, 'location': location, 'start_time': time(19, 0), }
        attended = [ClassOffer.objects.create(subject=subj, **kwargs) for subj in subjs]
        model.taken.add(*attended)

        self.assertTrue(model.beg.get('done'))
        self.assertEqual(model.compute_level(), 2)

    def test_level_methods_when_no_l2_attended(self):
        model = self.instance
        self.assertFalse(model.l2.get('done'))

    def test_level_methods_when_some_l2_attended(self):
        model = self.instance
        level = Subject.LEVEL_CHOICES[1][0]
        versions = ('A', 'B', )
        subjs = [Subject.objects.create(level=level, version=ver, title=f"{level}_{ver}_test", ) for ver in versions]
        level = Subject.LEVEL_CHOICES[0][0]
        subjs += [Subject.objects.create(level=level, version=ver, title=f"{level}_{ver}_test", ) for ver in versions]
        session = Session.objects.create(name='test_sess', key_day_date=date(2020, 1, 9))
        location = Location.objects.create(name='test_location', code='tl', address='12 main st', zipcode=98112, )
        kwargs = {'session': session, 'location': location, 'start_time': time(19, 0), }
        attended = [ClassOffer.objects.create(subject=subj, **kwargs) for subj in subjs]
        model.taken.add(*attended)

        self.assertFalse(model.l2.get('done'))
        self.assertTrue(model.beg.get('done'))
        self.assertEqual(model.compute_level(), 2)

    def test_level_methods_when_attended_l2_goal(self):
        model = self.instance
        level = Subject.LEVEL_CHOICES[1][0]
        versions = ('A', 'B', 'C', 'D', )
        subjs = [Subject.objects.create(level=level, version=ver, title=f"{level}_{ver}_test", ) for ver in versions]
        session = Session.objects.create(name='test_sess', key_day_date=date(2020, 1, 9))
        location = Location.objects.create(name='test_location', code='tl', address='12 main st', zipcode=98112, )
        kwargs = {'session': session, 'location': location, 'start_time': time(19, 0), }
        attended = [ClassOffer.objects.create(subject=subj, **kwargs) for subj in subjs]
        model.taken.add(*attended)
        expected = {'done': True}
        expected.update({key: 0 for key, string in Subject.VERSION_CHOICES if key not in ('N', )})

        self.assertTrue(model.l2.get('done'))
        self.assertEquals(model.l2, expected)
        self.assertEqual(model.compute_level(), 2.5)

    def test_level_methods_when_attended_double_l2_goal(self):
        model = self.instance
        level = Subject.LEVEL_CHOICES[1][0]
        versions = ('A', 'B', 'C', 'D', )
        subjs = [Subject.objects.create(level=level, version=ver, title=f"{level}_{ver}_test", ) for ver in versions]
        session = Session.objects.create(name='test_sess', key_day_date=date(2020, 1, 9))
        location = Location.objects.create(name='test_location', code='tl', address='12 main st', zipcode=98112, )
        kwargs = {'session': session, 'location': location, 'start_time': time(19, 0), }
        attended = [ClassOffer.objects.create(subject=subj, **kwargs) for subj in subjs]
        kwargs['session'] = Session.objects.create(name='test_sess2')  # Determines key_day_date based on previous
        attended += [ClassOffer.objects.create(subject=subj, **kwargs) for subj in subjs]
        model.taken.add(*attended)
        expected = {'done': True}
        expected.update({key: 1 for key, string in Subject.VERSION_CHOICES if key not in ('N', )})

        self.assertTrue(model.l2.get('done'))
        self.assertEquals(model.l2, expected)
        self.assertEqual(model.compute_level(), 3)

    def test_level_methods_when_no_l3_attended(self):
        model = self.instance
        self.assertFalse(model.l3.get('done'))

    def test_level_methods_when_some_l3_attended(self):
        model = self.instance
        level = Subject.LEVEL_CHOICES[2][0]
        versions = ('C', 'D', )
        subjs = [Subject.objects.create(level=level, version=ver, title=f"{level}_{ver}_test", ) for ver in versions]
        session = Session.objects.create(name='test_sess', key_day_date=date(2020, 1, 9))
        location = Location.objects.create(name='test_location', code='tl', address='12 main st', zipcode=98112, )
        kwargs = {'session': session, 'location': location, 'start_time': time(19, 0), }
        attended = [ClassOffer.objects.create(subject=subj, **kwargs) for subj in subjs]
        model.taken.add(*attended)

        self.assertFalse(model.l3.get('done'))

    def test_level_methods_when_attended_l3_goal(self):
        model = self.instance
        level = Subject.LEVEL_CHOICES[2][0]
        versions = ('A', 'B', 'C', 'D', )
        subjs = [Subject.objects.create(level=level, version=ver, title=f"{level}_{ver}_test", ) for ver in versions]
        session = Session.objects.create(name='test_sess', key_day_date=date(2020, 1, 9))
        location = Location.objects.create(name='test_location', code='tl', address='12 main st', zipcode=98112, )
        kwargs = {'session': session, 'location': location, 'start_time': time(19, 0), }
        attended = [ClassOffer.objects.create(subject=subj, **kwargs) for subj in subjs]
        model.taken.add(*attended)
        expected = {'done': True}
        expected.update({key: 0 for key, string in Subject.VERSION_CHOICES if key not in ('N', )})

        self.assertTrue(model.l3.get('done'))
        self.assertEquals(model.l3, expected)
        self.assertEqual(model.compute_level(), 3.5)

    def test_level_methods_when_attended_double_l3_goal(self):
        model = self.instance
        level = Subject.LEVEL_CHOICES[2][0]
        versions = ('A', 'B', 'C', 'D', )
        subjs = [Subject.objects.create(level=level, version=ver, title=f"{level}_{ver}_test", ) for ver in versions]
        session = Session.objects.create(name='test_sess', key_day_date=date(2020, 1, 9))
        location = Location.objects.create(name='test_location', code='tl', address='12 main st', zipcode=98112, )
        kwargs = {'session': session, 'location': location, 'start_time': time(19, 0), }
        attended = [ClassOffer.objects.create(subject=subj, **kwargs) for subj in subjs]
        session2 = Session.objects.create(name='test_sess2')
        kwargs['session'] = session2
        attended += [ClassOffer.objects.create(subject=subj, **kwargs) for subj in subjs]
        model.taken.add(*attended)
        expected = {'done': True}
        expected.update({key: 1 for key, string in Subject.VERSION_CHOICES if key not in ('N', )})

        self.assertTrue(model.l3.get('done'))
        self.assertEquals(model.l3, expected)
        self.assertEqual(model.compute_level(), 4)

    def test_profile_and_user_same_username(self):
        model = Profile.objects.first()
        user = UserHC.objects.first()
        expected = user.username
        self.assertEqual(model.user, user)
        self.assertEqual(model.username, expected)

    def test_profile_and_user_same_full_name(self):
        model = self.instance
        user = UserHC.objects.first()
        expected = user.full_name
        self.assertEqual(model.user, user)
        self.assertEqual(model.full_name, expected)

    def test__profile_and_user_same_get_full_name(self):
        model = self.instance
        user = UserHC.objects.first()
        expected = user.get_full_name()
        self.assertEqual(model.user, user)
        self.assertEqual(model.get_full_name(), expected)

    def test_subject_data_invalid_level_parameter(self):
        model = self.instance
        level = 'letters'
        with self.assertRaises(TypeError):
            model.subject_data(level=level)

    def test_subject_data_invalid_only_parameter(self):
        model = self.instance
        only = {'first': 'bad input', 'second': 'should not work'}
        with self.assertRaises(TypeError):
            model.subject_data(only=only)

    def test_subject_data_invalid_exclude_parameter(self):
        model = self.instance
        exclude = {'first': 'bad input', 'second': 'should not work'}
        with self.assertRaises(TypeError):
            model.subject_data(exclude=exclude)

    def test_subject_data_invalid_goal_map_parameter(self):
        model = self.instance
        goal_map = 'letters'
        with self.assertRaises(TypeError):
            model.subject_data(goal_map=goal_map)

    def test_subject_data_invalid_ver_map_parameter(self):
        model = self.instance
        ver_map = 'letters'
        with self.assertRaises(TypeError):
            model.subject_data(ver_map=ver_map)

    def test_subject_data_ver_map_with_invalid_type_values(self):
        model = self.instance
        ver_map = {0: 'bad input', 1: 'should not work'}
        with self.assertRaises(TypeError):
            model.subject_data(ver_map=ver_map)

    def test_subject_data_ver_map_has_list_values(self):
        model = self.instance
        level = Subject.LEVEL_CHOICES[0][0]
        versions = [first for first, second in Subject.VERSION_CHOICES]
        subjs = [Subject.objects.create(level=level, version=ver, title=f"{level}_{ver}_test", ) for ver in versions]
        session = Session.objects.create(name='test_sess', key_day_date=date(2020, 1, 9))
        location = Location.objects.create(name='test_location', code='tl', address='12 main st', zipcode=98112, )
        kwargs = {'session': session, 'location': location, 'start_time': time(19, 0), }
        attended = [ClassOffer.objects.create(subject=subj, **kwargs) for subj in subjs]
        model.taken.add(*attended)

        ver_map = {'A': ['A', 'C'], 'B': ['B', 'D']}
        level, each_ver = 0, 1
        goal, data, extra = model.subject_data(level=level, each_ver=each_ver, ver_map=ver_map)
        expected_goal = {key: each_ver for key in ver_map}
        expected_data = {key: 2 for key in ver_map}
        expected_extra = {key: 1 for key in ver_map}
        expected_extra['done'] = True

        self.assertDictEqual(expected_goal, goal)
        self.assertDictEqual(expected_data, data)
        self.assertDictEqual(expected_extra, extra)

    def test_subject_data_ver_map_has_dict_values(self):
        model = self.instance
        versions = [first for first, second in Subject.VERSION_CHOICES]
        subjs = []
        for level, string in Subject.LEVEL_CHOICES:
            subjs += [Subject.objects.create(level=level, version=ver, title=f"{level}_{ver}", ) for ver in versions]
        session = Session.objects.create(name='test_sess', key_day_date=date(2020, 1, 9))
        location = Location.objects.create(name='test_location', code='tl', address='12 main st', zipcode=98112, )
        kwargs = {'session': session, 'location': location, 'start_time': time(19, 0), }
        attended = [ClassOffer.objects.create(subject=subj, **kwargs) for subj in subjs]
        kwargs['session'] = Session.objects.create(name='test_sess2')  # Determines key_day_date based on previous
        attended += [ClassOffer.objects.create(subject=subj, **kwargs) for subj in subjs]
        model.taken.add(*attended)
        expected_taken_count = 2 * len(Subject.LEVEL_CHOICES) * len(Subject.VERSION_CHOICES)

        ver_map = {
            'early_beg': {
                'session': session,
                'subject__level': Subject.LEVEL_CHOICES[0][0]
            },
            'late_l2': {
                'session__name': 'test_sess2',
                'subject__level': Subject.LEVEL_CHOICES[1][0]
            },
            'early_l3': {
                'session': session,
                'subject__level': Subject.LEVEL_CHOICES[2][0]
            },
        }
        each_ver = 1
        expected_goal = {key: each_ver for key in ver_map}
        expected_data = {key: len(Subject.VERSION_CHOICES) for key in ver_map}
        expected_extra = {key: expected_data[key] - expected_goal[key] for key in ver_map}
        expected_extra['done'] = True
        goal, data, extra = model.subject_data(each_ver=each_ver, ver_map=ver_map)

        self.assertEqual(expected_taken_count, len(attended))
        self.assertEqual(expected_taken_count, model.taken.count())
        self.assertDictEqual(expected_goal, goal)
        self.assertDictEqual(expected_extra, extra)
        self.assertDictEqual(expected_data, data)

    def test_subject_data_ver_map_has_dict_values_with_or_combine_type(self):
        model = self.instance
        versions = [first for first, second in Subject.VERSION_CHOICES]
        subjs = []
        for level, string in Subject.LEVEL_CHOICES:
            subjs += [Subject.objects.create(level=level, version=ver, title=f"{level}_{ver}", ) for ver in versions]
        session = Session.objects.create(name='test_sess', key_day_date=date(2020, 1, 9))
        location = Location.objects.create(name='test_location', code='tl', address='12 main st', zipcode=98112, )
        kwargs = {'session': session, 'location': location, 'start_time': time(19, 0), }
        attended = [ClassOffer.objects.create(subject=subj, **kwargs) for subj in subjs]
        kwargs['session'] = Session.objects.create(name='test_sess2')  # Determines key_day_date based on previous
        attended += [ClassOffer.objects.create(subject=subj, **kwargs) for subj in subjs]
        model.taken.add(*attended)
        expected_taken_count = 2 * len(Subject.LEVEL_CHOICES) * len(Subject.VERSION_CHOICES)

        ver_map = {
            'previous_or_beg': {
                'session': session,
                'subject__level': Subject.LEVEL_CHOICES[0][0],
                'combine_type': 'OR'
            },
            'recent_or_l2': {
                'session__name': 'test_sess2',
                'subject__level': Subject.LEVEL_CHOICES[1][0],
                'combine_type': 'or'
            },
            'early_l3': {
                'session': session,
                'subject__level': Subject.LEVEL_CHOICES[2][0]
            },
        }
        each_ver = 1
        expected_goal = {key: each_ver for key in ver_map}
        expected_data = {key: len(Subject.VERSION_CHOICES) for key in ver_map}
        expected_extra = {key: expected_data[key] - expected_goal[key] for key in ver_map}
        expected_extra['done'] = True
        goal, data, extra = model.subject_data(each_ver=each_ver, ver_map=ver_map)

        self.assertEqual(expected_taken_count, len(attended))
        self.assertEqual(expected_taken_count, model.taken.count())
        self.assertDictEqual(expected_goal, goal)
        self.assertDictEqual(expected_extra, extra)
        self.assertDictEqual(expected_data, data)

    def test_subject_data_only_as_int_and_optional_parameters_as_none(self):
        model = self.instance
        versions = [first for first, second in Subject.VERSION_CHOICES]
        subjs = []
        for level, string in Subject.LEVEL_CHOICES:
            subjs += [Subject.objects.create(level=level, version=ver, title=f"{level}_{ver}", ) for ver in versions]
        session = Session.objects.create(name='test_sess', key_day_date=date(2020, 1, 9))
        location = Location.objects.create(name='test_location', code='tl', address='12 main st', zipcode=98112, )
        kwargs = {'session': session, 'location': location, 'start_time': time(19, 0), }
        attended = [ClassOffer.objects.create(subject=subj, **kwargs) for subj in subjs]
        kwargs['session'] = Session.objects.create(name='test_sess2')  # Determines key_day_date based on previous
        attended += [ClassOffer.objects.create(subject=subj, **kwargs) for subj in subjs]
        model.taken.add(*attended)

        level, each_ver, only, exclude = 0, 1, 0, None
        goal, data, extra = model.subject_data(level=level, each_ver=each_ver, only=only, exclude=exclude)
        clean_key = Subject.VERSION_CHOICES[only][0]
        expected_goal = {clean_key: each_ver}
        expected_data = {clean_key: 2}
        expected_extra = {clean_key: 2 - each_ver, 'done': True}

        self.assertDictEqual(expected_goal, goal)
        self.assertDictEqual(expected_data, data)
        self.assertDictEqual(expected_extra, extra)

    def test_subject_data_only_is_none_goal_map_given(self):
        model = self.instance
        versions = [first for first, second in Subject.VERSION_CHOICES]
        subjs = []
        for level, string in Subject.LEVEL_CHOICES:
            subjs += [Subject.objects.create(level=level, version=ver, title=f"{level}_{ver}", ) for ver in versions]
        session = Session.objects.create(name='test_sess', key_day_date=date(2020, 1, 9))
        location = Location.objects.create(name='test_location', code='tl', address='12 main st', zipcode=98112, )
        kwargs = {'session': session, 'location': location, 'start_time': time(19, 0), }
        attended = [ClassOffer.objects.create(subject=subj, **kwargs) for subj in subjs]
        kwargs['session'] = Session.objects.create(name='test_sess2')  # Determines key_day_date based on previous
        attended += [ClassOffer.objects.create(subject=subj, **kwargs) for subj in subjs]
        model.taken.add(*attended)

        goal_map, expected_goal = {}, {}
        for num, (ver, _val) in enumerate(Subject.VERSION_CHOICES, start=0):
            expected_goal[ver] = goal_map[num] = 1 if num % 2 else 2
        expected_data = {key: 2 for key in expected_goal}
        expected_extra = {key: 2 - val for key, val in expected_goal.items()}
        expected_extra['done'] = True
        level, exclude = 1, None
        goal, data, extra = model.subject_data(level=level, exclude=exclude, goal_map=goal_map)

        self.assertDictEqual(expected_goal, goal)
        self.assertDictEqual(expected_data, data)
        self.assertDictEqual(expected_extra, extra)

    @skip("Not Implemented yet")
    def test_subject_data_goal_map_as_dict(self):
        pass


class PaymentModelTests(SimpleModelTests, TestCase):
    Model = Payment
    repr_dict = {'Payment': '_payment_description'}
    str_list = ['_payment_description']
    defaults = {}


USER_DEFAULTS = {'email': 'user_fake@fakesite.com', 'password': '1234', 'first_name': 'f_user', 'last_name': 'fake_y'}


class UserModelTests(SimpleModelTests, TestCase):
    Model = UserHC
    repr_dict = {'UserHC': 'full_name'}
    str_list = ['full_name']
    create_method_name = 'create_user'
    defaults = USER_DEFAULTS.copy()


class UserModelNoNameTests(UserModelTests):
    defaults = {k: v for k, v in USER_DEFAULTS.items() if k not in ('first_name', 'last_name')}


class UserSuperModelTests(UserModelTests):
    create_method_name = 'create_superuser'


class UserSuperModelNoNameTests(UserModelTests):
    create_method_name = 'create_superuser'
    defaults = {k: v for k, v in USER_DEFAULTS.items() if k not in ('first_name', 'last_name')}


class UserExtendedModelTests(UserModelTests):

    @skip("Not Implemented")
    def test_get_if_only_one_function(self):
        pass

    @skip("Not Implemented")
    def test_value_error_normalize_email(self):
        pass

    @skip("Not Implemented")
    def test_set_user_no_email(self):
        pass

    @skip("Not Implemented")
    def test_set_existing_email_user(self):
        pass

    @skip("Not Implemented")
    def test_set_user_not_email_is_username(self):
        pass

    @skip("Not Implemented")
    def test_create_user_teacher(self):
        pass

    @skip("Not Implemented")
    def test_create_user_admin(self):
        pass

    @skip("Not Implemented")
    def test_create_superuser_not_staff(self):
        pass

    @skip("Not Implemented")
    def test_create_superuser_not_superuser(self):
        pass

    @skip("Not Implemented")
    def test_find_or_create_anon(self):
        pass

    @skip("Not Implemented")
    def test_find_or_create_name(self):
        pass

    @skip("Not Implemented")
    def test_make_username_use_email(self):
        pass

    @skip("Not Implemented")
    def test_make_username_not_use_email(self):
        pass

    @skip("Not Implemented")
    def test_save_with_no_username(self):
        pass

# end class UserExtendedModelTests


INITIAL = {
    "name": "May_2020",
    "key_day_date": "2020-04-30",
    "max_day_shift": -2,
    "num_weeks": 5,
    "expire_date": "2020-05-08",
    }


class RegistrationModelTests(SimpleModelTests, TestCase):
    Model = Registration
    repr_dict = {'Registration': 'classoffer', 'User': '_get_full_name', 'Owed': '_pay_report'}
    str_list = ['_get_full_name', 'classoffer', '_pay_report']
    defaults = {}
    related = {'student': Profile, 'classoffer': ClassOffer}

    @skip("Not Implemented")
    def test_owed_full_if_no_payment(self):
        pass

    @skip("Not Implemented")
    def test_owed_zero_if_in_person_payment(self):
        pass

    @skip("Not Implemented")
    def test_owed_zero_if_paid_correctly_in_advance(self):
        pass

    @skip("Not Implemented")
    def test_owed_remainder_on_partial_payment(self):
        pass

    @skip("Not Implemented")
    def test_owed_pre_discount_if_paid_after_deadline(self):
        pass

    @skip("Not Implemented")
    def test_first_name(self):
        pass

    @skip("Not Implemented")
    def test_last_name(self):
        pass

    @skip("Not Implemented")
    def test_get_full_name(self):
        pass

    @skip("Not Implemented")
    def test_credit_if_zero(self):
        pass

    @skip("Not Implemented")
    def test_credit_if_some(self):
        pass

    @skip("Not Implemented")
    def test_reg_class_is_subject(self):
        pass

    @skip("Not Implemented")
    def test_session_is_classoffer_session(self):
        pass

    @skip("Not Implemented")
    def test_class_day(self):
        pass

    @skip("Not Implemented")
    def test_start_time(self):
        pass


class NotifyModelTests(TestCase):
    Model = Notify
    repr_dict = {'Notify': 'name'}
    str_list = {}
    # TODO: Figure out values for SimpleModelTests and/or write other tests.


class SessionCoverageTests(TransactionTestCase):
    fixtures = ['tests/fixtures/db_basic.json', 'tests/fixtures/db_hidden.json']

    def create_session(self, **kwargs):
        obj = Session.objects.create(**kwargs)
        # obj.refresh_from_db()
        return obj

    def test_default_date_error_on_wrong_fields(self):
        session = Session.objects.get(id=1)
        with self.assertRaises(ValueError):
            session._default_date('expire_date')

    def test_default_date_traverse_prev_for_final_session(self):
        first = Session.objects.first()  # key_day_date = "2020-04-30", num_weeks = 5
        minimum_session_weeks = settings.SESSION_MINIMUM_WEEKS
        second = self.create_session(name="short_session", num_weeks=(minimum_session_weeks - 1))
        second.save()
        expected_key_day = first.key_day_date + timedelta(days=7*(first.num_weeks + first.break_weeks))
        third = self.create_session(name="third_test")
        third.save()

        self.assertGreater(minimum_session_weeks, 1)  # Otherwise we probably have error on create of second.
        self.assertEqual(first.skip_weeks, 0)  # Therefore, expected_key_day should be correct.
        self.assertGreater(third.start_date, first.end_date)
        self.assertEquals(third.publish_date, first.expire_date)
        self.assertEquals(expected_key_day, third.key_day_date)

    def test_compute_expire_day_with_key_day_none(self):
        session = Session.objects.get(id=1)
        computed_expire = session.computed_expire_day()
        self.assertEquals(session.expire_date, computed_expire)

    def test_clean_determine_date_from_previous(self):
        first = Session.objects.first()  # key_day_date = "2020-04-30", num_weeks = 5
        second = self.create_session(name="second_test")
        second.save()
        first_key_day = first.key_day_date  # 2020-04-30
        collide_key_day = first_key_day + timedelta(days=7*(first.num_weeks - 1))
        third = self.create_session(name="third_test", key_day_date=collide_key_day)
        third.save(with_clean=True)

        self.assertGreater(first.num_weeks, 1)
        self.assertGreater(third.start_date, second.end_date)
        self.assertGreater(second.start_date, first.end_date)

    def test_repr(self):
        session = Session.objects.first()
        repr_string = f"<Session: {session.name} >"
        self.assertEquals(repr_string, repr(session))

    def test_create_no_default_functions_no_shift(self):
        """ Session.create works with defined 'key_day_date' and 'publish_date'. """
        key_day = date.today() - timedelta(days=1)
        day_adjust, duration = 0, 5
        publish = key_day - timedelta(days=7*(duration - 1)+1)
        expire = key_day + timedelta(days=8)
        sess = self.create_session(
            name='t1_no_shift',
            key_day_date=key_day,
            max_day_shift=day_adjust,
            num_weeks=duration,
            publish_date=publish,
        )
        self.assertTrue(isinstance(sess, Session))
        self.assertEqual(sess.__str__(), sess.name)
        self.assertEquals(sess.start_date, sess.key_day_date)
        self.assertEquals(sess.publish_date, publish)
        self.assertEquals(sess.expire_date, expire)
        self.assertEquals(sess.end_date, key_day + timedelta(days=7*(duration - 1)))

    def test_session_defaults_on_creation(self):
        """ Session.create works with the date default functions in the model. """
        day_adjust, duration = 0, 5
        key_day = date.fromisoformat(INITIAL['key_day_date']) + timedelta(days=7*INITIAL['num_weeks'])
        new_publish_date = date.fromisoformat(INITIAL['expire_date'])
        expire = key_day + timedelta(days=8)
        end = key_day + timedelta(days=7*(duration - 1))
        sess = self.create_session(
            name='t2_no_shift',
            max_day_shift=day_adjust,
            num_weeks=duration,
        )
        self.assertEquals(sess.key_day_date, key_day)
        self.assertEquals(sess.start_date, key_day)
        self.assertEquals(sess.publish_date, new_publish_date)
        self.assertEquals(sess.expire_date, expire)
        self.assertEquals(sess.end_date, end)
        self.assertEquals(sess.prev_session.name, INITIAL['name'])
        self.assertEquals(sess.prev_session.expire_date, sess.publish_date)
        self.assertLess(sess.prev_session.end_date, sess.start_date)

    def test_create_early_shift_no_skip(self):
        """ Sessions with negative 'max_day_shift' correctly compute their dates. """
        day_adjust, duration = INITIAL['max_day_shift'], INITIAL['num_weeks']
        key_day = date.fromisoformat(INITIAL['key_day_date']) + timedelta(days=7*duration)
        publish = date.fromisoformat(INITIAL['expire_date'])
        expire = key_day + timedelta(days=8)
        start = key_day + timedelta(days=day_adjust)
        end = key_day + timedelta(days=7*(duration - 1))
        sess = self.create_session(
            name='t1_early_shift',
            max_day_shift=day_adjust,
            num_weeks=duration,
        )
        self.assertEquals(sess.key_day_date, key_day)
        self.assertEquals(sess.publish_date, publish)
        self.assertEquals(sess.expire_date, expire)
        self.assertEquals(sess.start_date, start)
        self.assertEquals(sess.start_date, sess.key_day_date + timedelta(days=day_adjust))
        self.assertEquals(sess.end_date, end)
        self.assertEquals(sess.prev_session.expire_date, sess.publish_date)
        self.assertLess(sess.prev_session.end_date, sess.start_date)

    def test_dates_late_shift_no_skip(self):
        """ Sessions with positive 'max_day_shift' correctly compute their dates. """
        day_adjust, duration = 5, INITIAL['num_weeks']
        key_day = date.fromisoformat(INITIAL['key_day_date']) + timedelta(days=7*duration)
        publish = date.fromisoformat(INITIAL['expire_date'])
        expire = key_day + timedelta(days=8+day_adjust)
        start = key_day
        end = key_day + timedelta(days=7*(duration - 1)+day_adjust)
        initial_end = date.fromisoformat(INITIAL['key_day_date']) + timedelta(days=7*(duration - 1))
        sess = self.create_session(
            name='t1_late_shift',
            max_day_shift=day_adjust,
            num_weeks=duration,
        )
        self.assertEquals(sess.key_day_date, key_day)
        self.assertEquals(sess.publish_date, publish)
        self.assertEquals(sess.expire_date, expire)
        self.assertEquals(sess.start_date, start)
        self.assertEquals(sess.end_date, end)
        self.assertLess(sess.prev_session.end_date, sess.start_date)
        self.assertEquals(sess.prev_session.end_date, initial_end)


# end of test.py file

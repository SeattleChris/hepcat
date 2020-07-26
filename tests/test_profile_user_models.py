from django.test import TestCase
# from django.conf import settings
from unittest import skip
from .helper import SimpleModelTests, AbstractProfileModelTests
from classwork.models import Location, Session, Subject, ClassOffer, Staff, Student
# from classwork.models import Resource, SiteContent, Payment, Registration, Notify
from users.models import UserHC
from datetime import date, time  # , timedelta, datetime as dt


class StaffModelTests(AbstractProfileModelTests, TestCase):
    Model = Staff
    profile_attribute = 'staff'


class StudentModelTests(AbstractProfileModelTests, TestCase):
    Model = Student
    profile_attribute = 'student'

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
        expected_data = {key: len(Subject.VERSION_CHOICES) for key in ver_map}  # TODO: Determine correct value
        expected_extra = {key: expected_data[key] - expected_goal[key] for key in ver_map}  # TODO: Determine value
        expected_extra['done'] = True

        with self.assertRaises(NotImplementedError):
            goal, data, extra = model.subject_data(each_ver=each_ver, ver_map=ver_map)
        self.assertEqual(expected_taken_count, len(attended))
        self.assertEqual(expected_taken_count, model.taken.count())
        # self.assertDictEqual(expected_goal, goal)
        # self.assertDictEqual(expected_extra, extra)
        # self.assertDictEqual(expected_data, data)

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

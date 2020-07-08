from django.test import TestCase, TransactionTestCase
from django.db.models import CharField, TextField, URLField, DateField, TimeField
from django.db.models import PositiveSmallIntegerField, SmallIntegerField
from django.db.models.fields import NOT_PROVIDED
# from .helper import SimpleModelTests
from classwork.models import Location, Resource, SiteContent, Subject, ClassOffer, Profile
from classwork.models import Session  # , Payment, Registration, Notify
# from users.models import UserHC
from datetime import date, time, timedelta
# from django.utils import timezone
# from django.core.urlresolvers import reverse
# from location.forms import WhateverForm
from pprint import pprint
from django.contrib.auth import get_user_model
User = get_user_model()

INITIAL = {
    "name": "May_2020",
    "key_day_date": "2020-04-30",
    "max_day_shift": -2,
    "num_weeks": 5,
    "expire_date": "2020-05-08",
}
# Create your tests here.


# class LocationModelTests(SimpleModelTests):
#     Model = Location


class LocationModelTests(TestCase):
    Model = Location
    repr_dict = {'Location': 'name', 'Link': 'map_google'}
    str_list = {'name'}
    defaults = {'name': "test model"}  # f"test {(str(Model).lower())}"
    skip_fields = ['date_added', 'date_modified']
    skip_attrs = {'auto_created': True, 'is_relation': True}

    def create_model(self, **kwargs):
        collected_kwargs = self.defaults.copy()
        collected_kwargs.update(kwargs)
        return self.Model.objects.create(**collected_kwargs)

    def repr_format(self, o):
        string_list = [f"{k}: {getattr(o, v, '')}" if k else str(getattr(o, v, '')) for k, v in self.repr_dict.items()]
        return '<' + ' | '.join(string_list) + ' >'

    def str_format(self, obj):
        string_list = [str(getattr(obj, field_name, '')) for field_name in self.str_list]
        return ' - '.join(string_list)

    def get_needed_fields(self):
        skips = self.skip_fields
        attrs = [key for key in self.skip_attrs]
        all_fields = self.Model._meta.fields
        fields = [f for f in all_fields if not any([f.name in skips, *[getattr(f, ea) for ea in attrs]])]
        return fields

    def get_field_info(self):
        fields = self.get_needed_fields()
        print(f'================================ {self.Model} get_field_info ============================')
        defaults = {}
        for field in fields:
            # print(f"------------- {field.name} -----------------")
            # pprint(dir(field))
            # pprint(field.choices)
            # pprint(field.max_length)
            if field.default is not NOT_PROVIDED:
                pass
            elif field.choices:
                defaults[field.name] = field.choices[0][0]
            elif isinstance(field, (CharField, TextField)):
                if field.name != 'name':
                    defaults[field.name] = 'test chars'
                    if field.max_length and field.max_length < len(defaults[field.name]):
                        defaults[field.name] = defaults[field.name][:field.max_length]
                if field.name == 'title':
                    initial = self.defaults.pop('name', defaults[field.name])
                    defaults[field.name] = self.defaults['title'] if 'title' in self.defaults else initial
            elif isinstance(field, URLField):
                defaults[field.name] = 'https://www.somewebsite.com/'
            elif isinstance(field, (PositiveSmallIntegerField, SmallIntegerField)):
                defaults[field.name] = 2
            elif isinstance(field, DateField):
                defaults[field.name] = date.today()
            elif isinstance(field, TimeField):
                defaults[field.name] = time(19, 0, 0)
            else:
                print(type(field))
        pprint(defaults)
        print('----------------------------------------')
        return defaults

    def test_model_creation(self):
        fields = self.get_field_info()
        model = self.create_model(**fields)
        repr_value = self.repr_format(model)
        str_value = self.str_format(model)

        self.assertIsInstance(model, self.Model)
        self.assertEqual(model.__str__(), str_value)
        self.assertEqual(model.__repr__(), repr_value)


class ResourceModelTests(LocationModelTests):
    Model = Resource
    repr_dict = {'Resource': 'content_type', '': 'avail'}
    str_list = {'title'}


class SiteContentModelTests(LocationModelTests):
    Model = SiteContent
    repr_dict = {'SiteContent': 'name'}
    str_list = {'name'}


class SubjectModelTests(LocationModelTests):
    Model = Subject
    repr_dict = {'Subject': 'title', 'Level': 'level', 'Version': 'version'}
    str_list = {'_str_slug'}
    # defaults = {'name': "test model"}


class SessionCoverageTests(TransactionTestCase):
    fixtures = ['tests/db_basic.json']

    def create_session(self, **kwargs):
        obj = Session.objects.create(**kwargs)
        # obj.refresh_from_db()
        return obj

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

# class LocationTests(TestCase):
#     """ The following are just examples. We normally don't have print, or test Django functionality itself. """

#     @classmethod
#     def setUpTestData(cls):
#         print("setUpTestData: Run once to set up non-modified data for all class methods.")
#         cls.first_place = Location.objects.create(
#             name='First Location',
#             code='fl',
#             address='123 Some St, #42',
#             zipcode='98112',
#             map_google='',
#             )
#         # city: use default 'Seattle'
#         # state: use default 'WA'

#     def setUp(self):
#         print("setUp: Run once for every test method to setup clean data.")
#         pass

#     def defaults_used(self):
#         self.assertEquals(self.first_place.city, 'Seattle')
#         self.assertEquals(self.first_place.state, 'WA')

#     def test_false_is_false(self):
#         print("Method: test_false_is_false.")
#         self.assertFalse(False)

#     def test_false_is_true(self):
#         print("Method: test_false_is_true.")
#         self.assertTrue(False)

#     def test_one_plus_one_equals_two(self):
#         print("Method: test_one_plus_one_equals_two.")
#         self.assertEqual(1 + 1, 2)

# end of test.py file

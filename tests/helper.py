from django.db.models.fields import NOT_PROVIDED
from django.db.models import CharField, TextField, URLField, DateField, TimeField
from django.db.models import PositiveSmallIntegerField, SmallIntegerField, base as db_models_base
from datetime import date, time  # , timedelta


class SimpleModelTests:
    Model = None
    repr_dict = {'ModelName': 'name'}
    str_list = ['name']
    defaults = {'name': "test model"}
    skip_fields = ['date_added', 'date_modified']
    skip_attrs = {'auto_created': True, 'is_relation': True}
    instance = None  # If not None, create_model will instead update this instance.
    related = {}  # If not empty, will be modified to have instance(s) of other related Model(s).
    create_method_name = 'create'

    def create_model(self, create_method_name='create', **kwargs):
        for field, target in self.related.items():
            RelatedModel, related_kwargs = None, None
            if isinstance(target, dict):
                RelatedModel = target.pop('RelatedModel', None)
                related_kwargs = target.copy()
            elif isinstance(target, db_models_base.ModelBase):
                RelatedModel = target
            else:
                print(type(target))
            if not RelatedModel:
                raise ValueError("Expected a Model in cls.related. ")
            q = RelatedModel.objects
            kwargs[field] = q.get_or_create(**related_kwargs) if related_kwargs else q.first()
        kwargs.update(self.defaults.copy())
        # collected_kwargs = self.defaults.copy()
        # collected_kwargs.update(kwargs)
        if self.instance:
            for key, value in kwargs.items():
                setattr(self.instance, key, value)
            self.instance.save()
            return self.instance
        # TODO: Refactor the following to actually retrieve the method on the model
        create_method = self.Model.objects
        if create_method_name == 'create':
            create_method = create_method.create
        elif create_method_name == 'create_user':
            create_method = create_method.create_user
        elif create_method_name == 'create_superuser':
            create_method = create_method.create_superuser
            password = kwargs.pop('password', None)
            email = kwargs.pop('email', None)
            username = kwargs.pop('username', email)
            return create_method(username, email, password, **kwargs)
        elif create_method_name == 'find_or_create_for_anon':
            create_method = create_method.find_or_create_for_anon
        elif create_method_name == 'find_or_create_by_name':
            create_method = create_method.find_or_create_by_name
        return create_method(**kwargs)

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
        defaults = {}
        for field in fields:
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
        return defaults

    def test_model_creation(self):
        fields = self.get_field_info()
        model = self.create_model(create_method_name=self.create_method_name, **fields)
        repr_value = self.repr_format(model)
        str_value = self.str_format(model)

        self.assertIsInstance(model, self.Model)
        self.assertEqual(model.__str__(), str_value)
        self.assertEqual(model.__repr__(), repr_value)


# class ExampleTests(TestCase):
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

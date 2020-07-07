from django.test import TestCase


class SimpleModelTests(TestCase):
    Model = None
    defaults = {'name': f"test {(str(Model).lower())}"}
    defaults['code'] = 'tst'
    defaults['address'] = '123 Some St, #42'
    defaults['zipcode'] = '98112'
    skip_fields = ['date_added', 'date_modified']

    def __init_subclass__(cls):
        return super().__init_subclass__()

    def __init__(self, methodName):
        super().__init__(methodName)

    def create_model(self, **kwargs):
        collected_kwargs = self.defaults.copy()
        collected_kwargs.update(kwargs)
        return self.Model.objects.create(**collected_kwargs)

    # def get_needed_fields(self):
    #     skip = self.skip_fields
    #     all_fields = self.Model._meta.fields
    #     fields = [field for field in all_fields if not any([field.name in skip, field.auto_created, field.is_relation])]
    #     return fields

    # def get_field_info(self):
    #     fields = self.get_needed_fields()
    #     info = [(field.name, field) for field in fields]
    #     return info

    def test_model_creation(self):
        model = self.create_model()
        self.assertIsInstance(model, self.Model)
        self.assertEqual(model.__str__(), model.name)
        for key, value in self.defaults.items():
            self.assertAlmostEquals(value, getattr(model, key, None))

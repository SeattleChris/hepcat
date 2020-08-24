# from django import forms
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.forms.utils import ErrorDict  # , ErrorList
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import AbstractBaseUser
from django_registration.forms import RegistrationForm
from django_registration import validators
from .models import UserHC


class BaseUserCreationForm(UserCreationForm):
    class Meta:
        model = UserHC
        fields = ['first_name', 'last_name', ]


class CustomUserCreationForm(BaseUserCreationForm):
    class Meta(BaseUserCreationForm.Meta):
        fields = ('first_name', 'last_name', 'email')  # 'uses_email_username',


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = UserHC
        fields = (
            'first_name', 'last_name',
            'email',
            'billing_address_1',
            'billing_address_2',
            'billing_city', 'billing_country_area', 'billing_postcode',
            'billing_country_code',
            )

    def as_person_details(self):

        pass

        # end as_person_details


class CustomRegistrationForm(RegistrationForm):

    class Meta(RegistrationForm.Meta):
        model = UserHC
        fields = ('first_name', 'last_name', model.USERNAME_FIELD, model.get_email_field_name(), 'uses_email_username',)
        computed_fields = (model.USERNAME_FIELD, 'uses_email_username', )
        case_insensitive = True
        unique_email = False

    # def __new__(cls, *args, **kwargs):
    #     print("========================= CustomRegistrationForm.__new__ ===============================")
    #     print(args)
    #     print(kwargs)
    #     instance = super(CustomRegistrationForm, cls).__new__(cls)
    #     print(instance)
    #     return instance

    def __init__(self, *args, **kwargs):
        from pprint import pprint
        if not hasattr(self.Meta, 'model') or not issubclass(self.Meta.model, AbstractBaseUser):
            err = "The model attribute must be a subclass of Django's AbstractBaseUser, AbstractUser, or User. "
            raise ImproperlyConfigured(_(err))
        # TODO: Refactor - above is done in the view. Here we should confirm needed functionality via hasattr.
        # must have self.model, self.model,USERNAME_FIELD, and implimented self.model.get_email_field_name()
        print("================================== CustomRegistrationForm.__init__ =====================")
        pprint(args)
        pprint(kwargs)
        super().__init__(*args, **kwargs)
        extracted_fields = {key: self.fields.pop(key, None) for key in self.Meta.computed_fields}
        self.computed_fields = extracted_fields
        # Set field validators, which will automatically be run at the start of the Field clean method.

        email_field = self.Meta.model.get_email_field_name()
        if email_field in self.fields:
            email_validators = [
                validators.HTML5EmailValidator(),
                validators.validate_confusables_email
            ]
            if self.Meta.unique_email:
                email_validators.append(
                    validators.CaseInsensitiveUnique(
                        self.Meta.model, email_field, validators.DUPLICATE_EMAIL
                    )
                )
            self.fields[email_field].validators.extend(email_validators)
            self.fields[email_field].required = True

        username = self.Meta.model.USERNAME_FIELD
        reserved_names = getattr(self, 'reserved_names', validators.DEFAULT_RESERVED_NAMES)
        username_validators = [
            validators.ReservedNameValidator(reserved_names),
            validators.validate_confusables,
        ]
        if self.Meta.case_insensitive:
            username_validators.append(
                validators.CaseInsensitiveUnique(
                    self.Meta.model, username, validators.DUPLICATE_USERNAME
                )
            )
        if username in self.computed_fields:
            self.computed_fields[username].validators.extend(username_validators)
        elif username in self.fields:
            self.fields[username].validators.extend(username_validators)

        print("---------------------------------------------------------")
        pprint(self.fields)
        pprint(self.computed_fields)

    def clean_username(self):
        # This is called if no ValidationError was raised by to_python(), validate(), or run_validators().
        print("=================== CustomRegistrationForm.clean_username ===========================")
        value = self.cleaned_data['username']
        return value  # Likely will not need this method.

    def compute_username(self):
        """ Set Field.initial as a str value or callable returning one. Overridden by self.initial['username']. """
        print("=================== CustomRegistrationForm.compute_username ===========================")
        model = self._meta.model
        username = model.USERNAME_FIELD
        field = self.computed_fields[username]
        result_value = self.cleaned_data[model.get_email_field_name()]
        lookup = {"{}__iexact".format(username): result_value}
        try:
            if model._default_manager.filter(**lookup).exists():
                names = (self.cleaned_data[key] for key in ('first_name', 'last_name') if self.cleaned_data.get(key))
                result_value = model.normalize_username('_'.join(names).casefold())
                self.initial['uses_email_username'] = False
        except Exception as e:
            print("Unable to query to lookup if this username exists. ")
            print(e)
        field.initial = result_value
        print(field.initial)
        return field

    def _clean_computed_fields(self):
        """ Mimics _clean_fields for computed_fields. Calls compute_<fieldname> and clean_<fieldname> if present. """
        compute_errors = ErrorDict()
        for name, field in self.computed_fields.items():
            # field.disabled = True  # field value will be self.get_initial_for_field(field, name)
            if hasattr(self, 'compute_%s' % name):
                field = getattr(self, 'compute_%s' % name)()
            self.computed_fields[name] = field  # self.fields[name] = field
            value = self.get_initial_for_field(field, name)
            try:
                value = field.clean(value)
                self.cleaned_data[name] = value
                if hasattr(self, 'clean_%s' % name):
                    value = getattr(self, 'clean_%s' % name)()
                    self.cleaned_data[name] = value
            except ValidationError as e:
                compute_errors[name] = e
                self.add_error(None, e)
        return compute_errors

    def clean(self):
        print("============================ CustomRegistrationForm.clean =========================")
        # cleaned_compute_data, compute_errors = self._clean_computed_fields()
        compute_errors = self._clean_computed_fields()
        print("---------------- compute_errors -----------------------------------------")
        print(compute_errors)
        if compute_errors:
            print("---------------- cleaned_computed_data -----------------------------------------")
            cleaned_compute_data = {name: self.cleaned_data.pop(name, None) for name in self.computed_fields}
            print(cleaned_compute_data)
            # print("- - - - - - - - - - - - - - - - - - - - - - - -")
        else:
            print(" We had no errors! ")
            self.fields.update(self.computed_fields)
        print("-----------------Cleaned Data After Cleaning Computed Fields -------------------------------------")
        print(self.cleaned_data)
        print("---------------------------------------------------------")
        return super().clean()

    def _post_clean(self):
        # This is after all form cleaning on self.fields. Now we do similar for self.computed_fields
        # Adding a field to self.fields will try to create an instance and use the Models validation methods.
        print("============================ CustomRegistrationForm._post_clean =========================")
        return super()._post_clean()

    def full_clean(self):
        print("============================ CustomRegistrationForm.full_clean =========================")
        return super().full_clean()

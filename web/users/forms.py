# from django import forms
from django.core.exceptions import ImproperlyConfigured
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
    class Meta:
        fields = ('first_name', 'last_name', 'email')  # 'uses_email_username',


class CustomUserChangeForm(UserChangeForm):
    class Meta:
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
        # pprint(self)
        pprint(args)
        pprint(kwargs)
        # # super(BaseUserCreationForm, self).__init__(*args, **kwargs)
        super().__init__(*args, **kwargs)
        extracted_fields = {key: self.fields.pop(key, None) for key in self.Meta.computed_fields}
        self.computed_fields = extracted_fields
        print("---------------------------------------------------------")
        pprint(self.fields)
        pprint(extracted_fields)

        email_field = self.Meta.model.get_email_field_name()
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
        if username in self.fields:
            self.fields[username].validators.extend(username_validators)
        else:
            self.computed_fields[username].validators.extend(username_validators)

        print("---------------------------------------------------------")
        pprint(self.fields)
        pprint(self.computed_fields)

    # def clean_username(self):

    #     pass

    #     # end clean_username

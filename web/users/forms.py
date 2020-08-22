# from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import AbstractBaseUser
from django_registration.forms import RegistrationForm
from django_registration import validators
from .models import UserHC


class CustomRegistrationForm(RegistrationForm):
    fields = ('first_name', 'last_name', )
    computed_fields = ('username', 'uses_email_username', )

    class Meta(RegistrationForm.Meta):
        model = UserHC
        case_insensitive = True
        unique_email = False

    def __init__(self, *args, **kwargs):
        if not hasattr(self, 'model') or not issubclass(self.model, AbstractBaseUser):
            err = "The model attribute must be a subclass of Django's AbstractBaseUser, AbstractUser, or User. "
            raise ImproperlyConfigured(_(err))
        # TODO: Refactor - above is done in the view. Here we should confirm needed functionality via hasattr.
        # must have self.model, self.model,USERNAME_FIELD, and implimented self.model.get_email_field_name()
        email_field = self.model.get_email_field_name()
        username = self.model.USERNAME_FIELD
        essential_fields = [username] if username not in getattr(self, 'computed_fields', []) else []
        essential_fields += [email_field, 'password1', 'password2', ]
        self.fields = list(getattr(self, 'fields', []))
        self.fields.extend([ea for ea in essential_fields if ea not in self.fields])

        super(UserCreationForm, self).__init__(*args, **kwargs)

        email_validators = [
            validators.HTML5EmailValidator(),
            validators.validate_confusables_email
        ]
        if self.unique_email:
            email_validators.append(
                validators.CaseInsensitiveUnique(
                    self.model, email_field, validators.DUPLICATE_EMAIL
                )
            )
        self.fields[email_field].validators.extend(email_validators)
        self.fields[email_field].required = True

        # reserved_names = getattr(self, 'reserved_names', validators.DEFAULT_RESERVED_NAMES)
        if hasattr(self, 'reserved_names'):
            reserved_names = self.reserved_names
        else:
            reserved_names = validators.DEFAULT_RESERVED_NAMES
        username_validators = [
            validators.ReservedNameValidator(reserved_names),
            validators.validate_confusables,
        ]
        if self.case_insensitive:
            username_validators.append(
                validators.CaseInsensitiveUnique(
                    self.model, username, validators.DUPLICATE_USERNAME
                )
            )
        if username in self.computed_fields:
            self.computed_fields[username].validators.extend(username_validators)
        else:
            self.fields[username].validators.extend(username_validators)

    def clean_username(self):

        pass

        # end clean_username


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = UserHC
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

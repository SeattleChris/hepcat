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
    confirmation = {'required': False, 'completed': False}

    class Meta(RegistrationForm.Meta):
        model = UserHC
        USERNAME_FLAG_FIELD = 'uses_email_username'
        fields = ('first_name', 'last_name', model.USERNAME_FIELD, model.get_email_field_name(), USERNAME_FLAG_FIELD, )
        computed_fields = (model.USERNAME_FIELD, USERNAME_FLAG_FIELD, )
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
        pprint(self.confirmation)
        initial_from_kwargs = kwargs.get('initial', {})
        initial_from_kwargs.update({self.Meta.model.USERNAME_FIELD: self.username_from_email_or_names})
        pprint(initial_from_kwargs)
        kwargs['initial'] = initial_from_kwargs
        super().__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs['autofocus'] = False
        extracted_fields = {key: self.fields.pop(key, None) for key in self.Meta.computed_fields}
        self.computed_fields = extracted_fields
        # TODO: Try - instead of extracting, set to hidden and disabled. Let self._clean_fields handle them.
        self.attach_critical_validators()
        print("---------------------------------------------------------")
        pprint(self.fields)
        pprint(self.computed_fields)

    def attach_critical_validators(self):
        """ The email and username fields have critical validators to be processed during field cleaning process. """
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

    def username_from_name(self):
        """ Must be evaluated after cleaned_data has 'first_name' and 'last_name' values populated. """
        names = (self.cleaned_data[key] for key in ('first_name', 'last_name') if self.cleaned_data.get(key))
        result_value = self._meta.model.normalize_username('_'.join(names).casefold())
        return result_value

    def username_from_email(self, username_field_name, email_field_name):
        """ Must be evaluated after cleaned_data has been populated with the the email field value. """
        if 'cleaned_data' not in self or email_field_name not in self.cleaned_data:
            if email_field_name in self.errors:
                result_value = None  # Or some technique to skip username validation without valid email?
            else:
                err = "This initial value can only be evaluated after fields it depends on have been cleaned. "
                err += "The field order must have {} after fields used for its value. ".format(username_field_name)
                raise ImproperlyConfigured(_(err))
        else:
            result_value = self.cleaned_data.get(email_field_name, None)
        return result_value

    def username_from_email_or_names(self, username_field_name, email_field_name):
        """ Initial username field value. Must be evaluated after dependent fields populate cleaned_data. """
        email_field_name = email_field_name or self._meta.model.get_email_field_name()
        username_field_name = username_field_name or self._meta.model.USERNAME_FIELD
        result_value = self.username_from_email(username_field_name, email_field_name)
        lookup = {"{}__iexact".format(username_field_name): result_value}
        try:
            if not result_value or self._meta.model._default_manager.filter(**lookup).exists():
                result_value = self.username_from_name()
                self.confirmation['required'] = True
        except Exception as e:
            print("Unable to query to lookup if this username exists. ")
            print(e)
        return result_value

    def configure_username_confirmation(self, field, username_field_name, email_field_name):
        """ Since the username is using the alternative computation, prepare form for user confirmation. """
        email_field_name = email_field_name or self._meta.model.get_email_field_name()
        username_field_name = username_field_name or self._meta.model.USERNAME_FIELD
        field = field or self.fields.get(username_field_name, None) or self.computed_fields.get(username_field_name)
        username_message = "You can use the suggested username or create your own. "
        field.help_text = _(username_message)
        field.widget.attrs['autofocus'] = False
        email_field = self.fields.pop(email_field_name, None) or self.computed_fields.pop(email_field_name, None)
        email_field.widget.attrs['autofocus'] = True
        flag_name = self._meta.USERNAME_FLAG_FIELD
        flag_field = self.computed_fields.pop(flag_name, None) or self.fields.pop(flag_name, None)
        self.initial[flag_name] = False

        self.fields[email_field_name] = email_field
        self.fields[flag_name] = flag_field
        self.fields[username_field_name] = field
        self.fields['password1'] = self.fields.pop('password1', None)
        self.fields['password2'] = self.fields.pop('password2', None)

        login_element = 'login'
        # TODO: Update 'login_element' as an HTML a element to link to login route.
        message = "Have you had classes or created an account using that email address? "
        message += "Go to {} to sign in with that account or reset the password if needed. ".format(login_element)
        message += "If you share an email with another student, then you will login with a username instead. "
        message += username_message
        self.add_error(None, _(message))  # Will be an error message at the top of the form.
        self.add_error(email_field_name, _("Username only needed if you do not have a unique email. "))
        self.add_error(flag_name, _("Use a unique email, or set a username for login use. "))
        return

    def clean_username(self):
        # This is called if no ValidationError was raised by to_python(), validate(), or run_validators().
        print("=================== CustomRegistrationForm.clean_username ===========================")
        value = self.cleaned_data['username']
        return value  # Likely will not need this method.

    def compute_username(self):
        """ Set Field.initial as a str value or callable returning one. Overridden by value in self.initial. """
        print("=================== CustomRegistrationForm.compute_username ===========================")
        model = self._meta.model
        username_field_name = model.USERNAME_FIELD
        field = self.computed_fields[username_field_name]
        email_field_name = model.get_email_field_name()
        result_value = self.username_from_email_or_names(username_field_name, email_field_name)
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
        compute_errors = self._clean_computed_fields()
        print("---------------- compute_errors -----------------------------------------")
        print(compute_errors)
        if compute_errors:
            print("---------------- cleaned_computed_data -----------------------------------------")
            cleaned_compute_data = {name: self.cleaned_data.pop(name, None) for name in self.computed_fields}
            print(cleaned_compute_data)
            raise ValidationError(_("Error occurred with the computed fields. "))
        elif self.confirmation['required']:
            print("- - - - - - - - - Confirmation Required - - - - - - - - - - - - - - -")
            self.configure_username_confirmation()
            message = "Login with existing account, change to a non-shared email, or create a username. "
            raise ValidationError(_(message))
        else:
            print(" Computed Fields had no problems! ")
            self.fields.update(self.computed_fields)
        print("--------------------- Cleaned Data After Cleaning Computed Fields ---------------------------------")
        cleaned_data = super().clean()  # return self.cleaned_data
        print(cleaned_data)
        print("---------------------- Initial data -------------------------------------------------")
        print(self.initial)
        if 'username' in self.fields:
            print(self.fields['username'].initial)
        print("---------------------------------------------------------")
        return cleaned_data

    def _post_clean(self):
        # This is after all form cleaning on self.fields. Now we do similar for self.computed_fields
        # Adding a field to self.fields will try to create an instance and use the Models validation methods.
        print("============================ CustomRegistrationForm._post_clean =========================")
        return super()._post_clean()

    def full_clean(self):
        print("============================ CustomRegistrationForm.full_clean =========================")
        return super().full_clean()

from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.forms.utils import ErrorDict  # , ErrorList
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django_registration.forms import RegistrationForm
from django_registration import validators
from collections import abc
from pprint import pprint  # Temporary for debug.
from .models import UserHC


class CustomRegistrationForm(RegistrationForm):
    confirmation = {'required': False, 'completed': False}

    class Meta(RegistrationForm.Meta):
        model = UserHC
        USERNAME_FLAG_FIELD = 'uses_email_username'
        fields = ('first_name', 'last_name', model.get_email_field_name(), USERNAME_FLAG_FIELD, model.USERNAME_FIELD, )
        computed_fields = (model.USERNAME_FIELD, USERNAME_FLAG_FIELD, )
        case_insensitive = True
        unique_email = False

    def __init__(self, *args, **kwargs):
        model = self.Meta.get('model', None)
        required_attributes = ('USERNAME_FIELD', 'get_email_field_name', 'is_active')
        if not model or not all(hasattr(model, ea) for ea in required_attributes):
            err = "Missing features for user model. Try subclassing Django's AbstractBaseUser, AbstractUser, or User. "
            raise ImproperlyConfigured(_(err))
        print("================================== CustomRegistrationForm.__init__ =====================")
        pprint(args)
        pprint(kwargs)
        pprint(self.confirmation)
        username_field_name = self.Meta.model.USERNAME_FIELD
        email_field_name = self.Meta.model.get_email_field_name()
        initial_from_kwargs = kwargs.get('initial', {})
        initial_from_kwargs.update({username_field_name: self.username_from_email_or_names})
        kwargs['initial'] = initial_from_kwargs
        super().__init__(*args, **kwargs)
        if username_field_name in self.fields:
            self.fields[username_field_name].widget.attrs['autofocus'] = False
        extracted_fields = {key: self.fields.pop(key, None) for key in self.Meta.computed_fields}
        self.computed_fields = extracted_fields
        # TODO: Try - instead of extracting, set to hidden and disabled. Let self._clean_fields handle them.
        self.attach_critical_validators()
        if self.confirmation['required'] and email_field_name in self.fields:
            self.fields[email_field_name].widget.attrs['autofocus'] = True
        else:
            self.focus_first_usable_field(self.fields.values())
        print("---------------------------------------------------------")
        pprint(self.fields)
        pprint(self.computed_fields)

    def focus_first_usable_field(self, fields):
        """ Gives autofocus to the first non-hidden, non-disabled form field from the given iterable of form fields. """
        if not isinstance(fields, (list, tuple, abc.ValuesView)):
            raise TypeError(_("Expected an iterable of form fields. "))
        field_gen = (ea for ea in fields)
        first_field = next(field_gen)
        while first_field.disabled or (hasattr(first_field, 'is_hidden') and first_field.is_hidden):
            if 'autofocus' in first_field.widget.attrs:
                first_field.widget.attrs['autofocus'] = False
            first_field = next(field_gen)
        first_field.widget.attrs['autofocus'] = True
        return first_field

    def attach_critical_validators(self):
        """ The email and username fields have critical validators to be processed during field cleaning process. """
        email_name = self.Meta.model.get_email_field_name()
        email_validators = [
            validators.HTML5EmailValidator(),
            validators.validate_confusables_email
        ]
        if self.Meta.unique_email:
            email_validators.append(
                validators.CaseInsensitiveUnique(
                    self.Meta.model, email_name, validators.DUPLICATE_EMAIL
                )
            )
        email_field = self.fields.get(email_name, None) or self.computed_fields.get(email_name, None)
        email_field.validators.extend(email_validators)
        email_field.required = True

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
        username_field = self.computed_fields.get(username, None) or self.fields.get(username, None)
        username_field.validators.extend(username_validators)

    def username_from_name(self):
        """ Must be evaluated after cleaned_data has 'first_name' and 'last_name' values populated. """
        print("=================== CustomRegistrationForm.username_from_name ===========================")
        if not hasattr(self, 'cleaned_data'):
            raise ImproperlyConfigured(_("This method can only be evaluated after 'cleaned_data' has been populated. "))
        names = (self.cleaned_data[key] for key in ('first_name', 'last_name') if self.cleaned_data.get(key))
        result_value = self._meta.model.normalize_username('_'.join(names).casefold())
        print(result_value)
        return result_value

    def username_from_email(self, username_field_name, email_field_name):
        """ Must be evaluated after cleaned_data has been populated with the the email field value. """
        print("=================== CustomRegistrationForm.username_from_email ===========================")
        if not hasattr(self, 'cleaned_data') or email_field_name not in self.cleaned_data:
            if email_field_name in self.errors:
                result_value = None  # TODO: ? Need some technique to skip username validation without valid email?
            else:
                err = "This initial value can only be evaluated after fields it depends on have been cleaned. "
                err += "The field order must have {} after fields used for its value. ".format(username_field_name)
                raise ImproperlyConfigured(_(err))
        else:
            result_value = self.cleaned_data.get(email_field_name, None)
        print(result_value)
        return result_value

    def username_from_email_or_names(self, username_field_name=None, email_field_name=None):
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

    def configure_username_confirmation(self, field=None, username_field_name=None, email_field_name=None):
        """ Since the username is using the alternative computation, prepare form for user confirmation. """
        email_field_name = email_field_name or self._meta.model.get_email_field_name()
        username_field_name = username_field_name or self._meta.model.USERNAME_FIELD
        field = field or self.fields.pop(username_field_name, None) or self.computed_fields.pop(username_field_name)
        username_message = "Use the suggested username or create your own. Only needed if using a shared email. "
        field.help_text = _(username_message)
        email_field = self.fields.pop(email_field_name, None) or self.computed_fields.pop(email_field_name, None)
        email_field.widget.attrs['autofocus'] = True
        flag_name = self.Meta.USERNAME_FLAG_FIELD
        flag_field = self.computed_fields.pop(flag_name, None) or self.fields.pop(flag_name, None)
        flag_field.help_text = _("Select if you're using a non-shared email. ")
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
        message += "If you share an email with another user, then you will login with a username instead. "
        self.add_error(None, _(message))  # Will be an error message at the top of the form.
        self.add_error(email_field_name, _("Use a non-shared email, or set a username below. "))
        # self.add_error(flag_name, _("Username only needed if you share an email with another user. "))
        # TODO: Check if true: Do not add_error for username_field, that way it still auto-populates the value.
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
        print("---------------------- value for username field.initial --------------------------- ")
        print(field.initial)
        return field

    def _clean_computed_fields(self):
        """ Mimics _clean_fields for computed_fields. Calls compute_<fieldname> and clean_<fieldname> if present. """
        compute_errors = ErrorDict()
        cleaned_data = getattr(self, 'cleaned_data', None)
        print("=================== CustomRegistrationForm._clean_computed_fields ============================")
        print(cleaned_data)
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
        cleaned_data = super().clean()  # return self.cleaned_data, also sets boolean for unique validation.
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


class CustomUserCreationForm(UserCreationForm):
    """ Deprecated, prefer CustomRegistrationForm. This will be removed after feature and integration are confirmed. """
    class Meta(UserCreationForm.Meta):
        model = UserHC
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.focus_first_usable_field(self, self.fields.values())

    def focus_first_usable_field(self, fields):
        """ Gives autofocus to the first non-hidden, non-disabled form field from the given iterable of form fields. """
        if not isinstance(fields, (list, tuple, abc.ValuesView)):
            raise TypeError(_("Expected an iterable of form fields. "))
        field_gen = (ea for ea in fields)
        first_field = next(field_gen)
        while first_field.disabled or (hasattr(first_field, 'is_hidden') and first_field.is_hidden):
            if 'autofocus' in first_field.widget.attrs:
                first_field.widget.attrs['autofocus'] = False
            first_field = next(field_gen)
        first_field.widget.attrs['autofocus'] = True
        return first_field

    def as_person_details(self):

        pass

        # end as_person_details

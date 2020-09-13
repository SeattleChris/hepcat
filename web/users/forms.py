from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.forms.utils import ErrorDict  # , ErrorList
from django.utils.translation import gettext as _
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django_registration.forms import RegistrationForm
# from django_registration import validators
from pprint import pprint  # TODO: Remove after debug.
from .models import UserHC
from .mixins import PersonFormMixIn, ExtractFieldsMixIn


class CustomRegistrationForm(PersonFormMixIn, ExtractFieldsMixIn, RegistrationForm):

    class Meta(RegistrationForm.Meta):
        model = UserHC
        USERNAME_FLAG_FIELD = 'username_not_email'
        fields = ('first_name', 'last_name', model.get_email_field_name(), USERNAME_FLAG_FIELD, model.USERNAME_FIELD, )
        computed_fields = (model.USERNAME_FIELD, USERNAME_FLAG_FIELD, )
        strict_username = True  # case_insensitive
        strict_email = False  # unique_email and case_insensitive
        help_texts = {
            model.USERNAME_FIELD: _("Without a unique email, a username is needed. Use suggested or create one. "),
            model.get_email_field_name(): _("Used for confirmation and typically for login"),
        }

    def __init__(self, *args, **kwargs):
        model = getattr(self._meta, 'model', None)
        required_attributes = ('USERNAME_FIELD', 'get_email_field_name', 'is_active')
        if not model or not all(hasattr(model, ea) for ea in required_attributes):
            err = "Missing features for user model. Try subclassing Django's AbstractBaseUser, AbstractUser, or User. "
            raise ImproperlyConfigured(_(err))
        print("================================== CustomRegistrationForm.__init__ =====================")
        username_field_name = self._meta.model.USERNAME_FIELD
        email_field_name = self._meta.model.get_email_field_name()
        named_focus = kwargs.get('named_focus', None)
        if username_field_name in kwargs.get('data', {}):
            named_focus = email_field_name
        kwargs['named_focus'] = named_focus
        kwargs['computed_fields'] = self.Meta.computed_fields
        kwargs['strict_email'] = self.Meta.strict_email
        kwargs['strict_username'] = self.Meta.strict_username
        super().__init__(*args, **kwargs)
        # TODO: If using RegistrationForm init, then much, but not all, of attach_critical_validators is duplicate code.
        print("--------------------- FINISH users.CustomRegistrationForm.__init__ --------------------")

    def username_from_name(self):
        """ Must be evaluated after cleaned_data has 'first_name' and 'last_name' values populated. """
        if not hasattr(self, 'cleaned_data'):
            raise ImproperlyConfigured(_("This method can only be evaluated after 'cleaned_data' has been populated. "))
        names = (self.cleaned_data[key].strip() for key in ('first_name', 'last_name') if self.cleaned_data.get(key))
        result_value = self._meta.model.normalize_username('_'.join(names).casefold())
        return result_value

    def username_from_email(self, username_field_name, email_field_name):
        """ Must be evaluated after cleaned_data has been populated with the the email field value. """
        if not hasattr(self, 'cleaned_data') or email_field_name not in self.cleaned_data:
            if hasattr(self, '_errors') and email_field_name in self._errors:
                result_value = None  # TODO: ? Need some technique to skip username validation without valid email?
            else:
                err = "This initial value can only be evaluated after fields it depends on have been cleaned. "
                err += "The field order must have {} after fields used for its value. ".format(username_field_name)
                raise ImproperlyConfigured(_(err))
        else:
            result_value = self.cleaned_data.get(email_field_name, None)
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
        except Exception as e:
            print("Unable to query to lookup if this username exists. ")
            print(e)
        return result_value

    def configure_username_confirmation(self, username_field_name=None, email_field_name=None):
        """ Since the username is using the alternative computation, prepare form for user confirmation. """
        username_field_name = username_field_name or self._meta.model.USERNAME_FIELD
        field = self.computed_fields.pop(username_field_name, None) or self.fields.pop(username_field_name, None)
        field.initial = self.cleaned_data.get(username_field_name, field.initial)
        email_field_name = email_field_name or self._meta.model.get_email_field_name()
        email_field = self.fields.pop(email_field_name, None) or self.computed_fields.pop(email_field_name, None)
        email_field.initial = self.cleaned_data.get(email_field_name, email_field.initial)
        flag_name = self.Meta.USERNAME_FLAG_FIELD
        flag_field = self.computed_fields.pop(flag_name, None) or self.fields.pop(flag_name, None)
        if flag_field:
            flag_field.initial = 'False'

        data = self.data.copy()  # QueryDict datastructure, the copy is mutable. Has getlist and appendlist methods.
        data.appendlist(email_field_name, email_field.initial)
        if flag_field:
            data.appendlist(flag_name, flag_field.initial)
        data.appendlist(username_field_name, field.initial)
        data._mutable = False
        self.data = data

        self.fields[email_field_name] = email_field
        self.fields[flag_name] = flag_field
        self.fields[username_field_name] = field
        self.fields['password1'] = self.fields.pop('password1', None)
        self.fields['password2'] = self.fields.pop('password2', None)
        self.assign_focus_field(name=email_field_name)  # TODO: How do we want to organize interconnected features.
        self.attach_critical_validators()

        login_link = self.get_login_message(link_text='login to existing account', link_only=True)
        text = "Use a non-shared email, or set a username below, or {}. ".format(login_link)
        self.add_error(email_field_name, mark_safe(_(text)))
        e_note = "Typically people have their own unique email address, which you can update. "
        e_note += "If you share an email with another user, then you will need to create a username for your login. "
        self.add_error(email_field_name, (_(e_note)))
        title = "Login with existing account, change to a non-shared email, or create a username. "
        message = "Did you already make an account, or have one because you've had classes with us before? "
        message = format_html(
            "<h3>{}</h3> <p>{} <br />{}</p>",  # <p>{}</p>
            _(title),
            _(message),
            self.get_login_message(reset=True),
            )
        return message

    def get_login_message(self, link_text=None, link_only=False, reset=False):
        """ Returns text with html links to login. If reset is True, the message includes a link for password reset. """
        link_text = _(link_text) if link_text else None
        login_link = format_html('<a href="{}">{}</a>', reverse('login'), link_text or _('login'))
        reset_link = format_html('<a href="{}">{}</a>', reverse('password_reset'), link_text or _('reset the password'))
        if link_only:
            return login_link if not reset else reset_link
        message = "You can {} to your existing account".format(login_link)
        if reset:
            message += " or {} if needed".format(reset_link)
        message += ". "
        return mark_safe(_(message))

    def compute_username(self):
        """ Determine a str value or callable returning one and set this in self.initial dict. """
        print("=================== CustomRegistrationForm.compute_username ===========================")
        model = self._meta.model
        username_field_name = model.USERNAME_FIELD
        field = self.computed_fields[username_field_name]
        email_field_name = model.get_email_field_name()
        result_value = self.username_from_email_or_names(username_field_name, email_field_name)
        self.initial[username_field_name] = field.initial = result_value
        return field

    def _clean_computed_fields(self):
        """ Mimics _clean_fields for computed_fields. Calls compute_<fieldname> and clean_<fieldname> if present. """
        compute_errors = ErrorDict()
        print("=================== CustomRegistrationForm._clean_computed_fields ============================")
        for name, field in self.computed_fields.items():
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

    def handle_flag_field(self, email_field_name, user_field_name):
        """ If the user gave a non-shared email, we expect flag is False, and no username value. """
        flag_name = self.Meta.USERNAME_FLAG_FIELD
        flag_field = self.fields.get(flag_name, None) or self.computed_fields.get(flag_name, None)
        print("==================== handle_flag_field =====================================")
        if not flag_field:
            print("No flag field")
            return
        flag_value = self.cleaned_data[flag_name]
        flag_prev = self.data.getlist(flag_name, [flag_field.initial])
        flag_changed = flag_field.has_changed(flag_prev[-1], flag_value)
        email_field = self.fields[email_field_name]
        email_value = self.cleaned_data[email_field_name]
        email_prev = self.data.getlist(email_field_name, [email_field.initial])
        email_changed = email_field.has_changed(email_prev[-1], email_value)
        user_field = self.fields[user_field_name]
        user_value = self.cleaned_data[user_field_name]
        user_prev = self.data.getlist(user_field_name, [user_field.initial])
        user_changed = user_field.has_changed(user_prev[-1], user_value)
        flag_data = f"Init: {flag_field.initial} | Prev: {flag_prev} | Clean: {flag_value} | New: {flag_changed} "
        email_data = f"Init: {email_field.initial} | Prev: {email_prev} | Clean: {email_value} | New: {email_changed} "
        user_data = f"Init: {user_field.initial} | Prev: {user_prev} | Clean: {user_value} | New: {user_changed} "
        pprint(flag_data)
        pprint(email_data)
        pprint(user_data)
        error_collected = {}
        if not flag_value:
            lookup = {"{}__iexact".format(user_field_name): email_value}
            try:
                if not email_changed or self._meta.model._default_manager.filter(**lookup).exists():
                    message = "You must give a unique email not shared with other users (or create a username). "
                    error_collected[email_field_name] = _(message)
            except Exception as e:
                print("Could not lookup if the new email is already used as a username. ")
                print(e)
            self.cleaned_data[user_field_name] = email_value
        elif email_changed:
            message = "Un-check the box, or leave empty, if you want to use this email address. "
            error_collected[flag_name] = _(message)
        return error_collected

    def clean(self):
        username_field_name = self._meta.model.USERNAME_FIELD
        username_value = self.cleaned_data.get(username_field_name, '')
        email_field_name = self._meta.model.get_email_field_name()
        email_value = self.cleaned_data.get(email_field_name, None)
        print("============================ CustomRegistrationForm.clean =========================")
        print("***********************************************************************************")
        for key, items in self.data.lists():
            print(f"{key}: {items} ")
        print("-----------------------------------------------------------------------------------")
        pprint(self.cleaned_data)
        print("***********************************************************************************")
        compute_errors = self._clean_computed_fields()
        print("---------------- compute_errors -----------------------------------------")
        print(compute_errors)
        if compute_errors:
            print("---------------- cleaned_computed_data -----------------------------------------")
            cleaned_compute_data = {name: self.cleaned_data.pop(name, None) for name in self.computed_fields}
            print(cleaned_compute_data)
            raise ValidationError(_("Error occurred with the computed fields. "))
        elif username_field_name not in self.data and username_value != email_value:
            print("- - - - - - - - - Confirmation Required - - - - - - - - - - - - - - -")
            marked_safe_translatable_html = self.configure_username_confirmation()
            print("---------------------- Form Data --------------------------------------")
            for key, items in self.data.lists():
                print(f"{key}: {items} ")
            raise ValidationError(marked_safe_translatable_html)
        else:
            print(" Computed Fields had no problems! ")
            self.fields.update(self.computed_fields)

        error_dict = self.handle_flag_field(email_field_name, username_field_name)
        if error_dict:
            print("We had an error processing the flag. ")
            raise ValidationError(error_dict)
        print("--------------------- Cleaned Data After Cleaning Computed Fields ---------------------------------")
        cleaned_data = super().clean()  # return self.cleaned_data, also sets boolean for unique validation.
        print(cleaned_data)
        print("---------------------------------------------------------")
        return cleaned_data


class CustomUserCreationForm(UserCreationForm):
    """ Deprecated, prefer CustomRegistrationForm. This will be removed after feature and integration are confirmed. """
    class Meta(UserCreationForm.Meta):
        model = UserHC
        fields = ('first_name', 'last_name', 'email')  # 'username_not_email',


class CustomUserChangeForm(PersonFormMixIn, UserChangeForm):
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
        # TODO: Integrate focus_correct_field method as a MixIn
        self.fields['billing_address_1'].widget.attrs['autofocus'] = True

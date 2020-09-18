from django import forms
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.contrib.admin.utils import flatten
from django.forms.widgets import Input, CheckboxInput, HiddenInput, Textarea
from django.forms.utils import ErrorDict  # , ErrorList
from django.utils.translation import gettext as _
from django.utils.html import conditional_escape, format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from django_registration import validators
# from . import validators
from .models import UserHC
from pprint import pprint


class FocusMixMin:
    """ Autofocus given to a field not hidden or disabled. Can limit to a fields subset, and prioritize a named one. """

    def __init__(self, *args, **kwargs):
        print("======================= Focus MixIn =================================")
        named_focus = kwargs.pop('named_focus', None)
        fields_focus = kwargs.pop('fields_focus', None)
        super().__init__(*args, **kwargs)
        named_focus = kwargs.pop('named_focus', named_focus)
        fields_focus = kwargs.pop('fields_focus', fields_focus)
        self.assign_focus_field(name=named_focus, fields=fields_focus)
        print("--------------------- Finish Focus MixIn --------------------")

    def assign_focus_field(self, name=None, fields=None):
        """ Autofocus only on the non-hidden, non-disabled named or first form field from the given or self fields. """
        name = name() if callable(name) else name
        fields = fields or self.fields
        found = fields.get(name, None) if name else None
        if found and (getattr(found, 'disabled', False) or getattr(found, 'is_hidden', False)):
            found = None
        for field_name, field in fields.items():
            if not found and not field.disabled and not getattr(field, 'is_hidden', False):
                found = field
            else:
                field.widget.attrs.pop('autofocus', None)
        if found:
            found.widget.attrs['autofocus'] = True
        return found


class ComputedFieldsMixIn:
    """ Allows for computed fields with optional user overrides triggered by validation checks. Should be last MixIn."""
    computed_fields = []
    reserved_names_replace = False
    # reserved_names = []

    def __init__(self, *args, **kwargs):
        print("======================= ComputedFieldsMixIn.__init__ =================================")
        validator_kwargs = kwargs.pop('validator_kwargs', {})
        self.attach_critical_validators(**validator_kwargs)
        computed_fields = kwargs.pop('computed_fields', getattr(self, 'computed_fields', []))
        super().__init__(*args, **kwargs)
        keep_keys = set(self.data.keys())
        if computed_fields:
            extracted_fields = {key: self.fields.pop(key, None) for key in set(computed_fields) - keep_keys}
            self.computed_fields = extracted_fields
        print("--------------------- FINISH ComputedFieldsMixIn.__init --------------------")

    def attach_critical_validators(self, **kwargs):
        """Before setting computed_fields, assign validators to the email and username fields. """
        fields = getattr(self, 'base_fields', None) if not hasattr(self, 'fields') else self.fields
        if not fields:
            raise ImproperlyConfigured(_("Any ComputedFieldsMixIn depends on access to base_fields or fields. "))
        if getattr(self, 'reserved_names_replace', False):
            reserved_names = getattr(self, 'reserved_names', validators.DEFAULT_RESERVED_NAMES)
        else:
            reserved_names = getattr(self, 'reserved_names', []) + validators.DEFAULT_RESERVED_NAMES

        username = getattr(self._meta.model, 'USERNAME_FIELD', None)
        if username and username in fields:
            username_validators = [
                validators.ReservedNameValidator(reserved_names),
                validators.validate_confusables,
            ]
            if kwargs.get('strict_username', None):
                username_validators.append(
                    validators.CaseInsensitiveUnique(
                        self._meta.model, username, validators.DUPLICATE_USERNAME
                    )
                )
            username_field = fields[username]
            username_field.validators.extend(username_validators)

        email_name = getattr(self._meta.model, 'get_email_field_name', None)
        email_name = email_name() if callable(email_name) else email_name
        if email_name and email_name in fields:
            email_validators = [
                validators.HTML5EmailValidator(),
                validators.validate_confusables_email
            ]
            if kwargs.get('strict_email', None):
                email_validators.append(
                    validators.CaseInsensitiveUnique(
                        self._meta.model, email_name, validators.DUPLICATE_EMAIL
                    )
                )
            email_field = fields[email_name]
            email_field.validators.extend(email_validators)
            email_field.required = True

    def field_computed_from_fields(self, field_names=None, joiner='_', normalize=None):
        """ Must be evaluated after cleaned_data has the named field values populated. """
        if not field_names:
            raise ImproperlyConfigured(_("There must me one or more field names to compute a value. "))
        if not hasattr(self, 'cleaned_data'):
            raise ImproperlyConfigured(_("This method can only be evaluated after 'cleaned_data' has been populated. "))
        if any(field not in self.cleaned_data for field in field_names):
            if hasattr(self, '_errors') and any(field in self._errors for field in field_names):
                return None  # TODO: ? Need some technique to skip username validation without valid email?
            err = "This initial value can only be evaluated after fields it depends on have been cleaned. "
            err += "The field order must have the computed field after fields used for its value. "
            raise ImproperlyConfigured(_(err))

        names = (self.cleaned_data[key].strip() for key in field_names if key in self.cleaned_data)
        result_value = joiner.join(names).casefold()
        if callable(normalize):
            result_value = normalize(result_value)
        elif normalize is not None:
            raise ImproperlyConfigured(_("The normalize parameter must be a callable or None. "))
        return result_value

    def _clean_computed_fields(self):
        """ Mimics _clean_fields for computed_fields. Calls compute_<fieldname> and clean_<fieldname> if present. """
        compute_errors = ErrorDict()
        # print("=================== CustomRegistrationForm._clean_computed_fields ============================")
        for name, field in self.computed_fields.items():
            if hasattr(self, 'compute_%s' % name):
                field = getattr(self, 'compute_%s' % name)()
            self.computed_fields[name] = field  # self.fields[name] = field
            value = self.get_initial_for_field(field, name)  # TODO: ? or check if it has a value set?
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
        # print("***********************************************************************************")
        # for key, items in self.data.lists():
        #     print(f"{key}: {items} ")
        # print("-----------------------------------------------------------------------------------")
        # pprint(self.cleaned_data)
        # print("***********************************************************************************")
        compute_errors = self._clean_computed_fields()
        print("---------------- compute_errors -----------------------------------------")
        print(compute_errors)
        if compute_errors:
            print("---------------- cleaned_computed_data -----------------------------------------")
            cleaned_compute_data = {name: self.cleaned_data.pop(name, None) for name in self.computed_fields}
            print(cleaned_compute_data)
            raise ValidationError(_("Error occurred with the computed fields. "))
        # print("--------------------- Cleaned Data After Cleaning Computed Fields ---------------------------------")
        cleaned_data = super().clean()  # return self.cleaned_data, also sets boolean for unique validation.
        # print(cleaned_data)
        # print("---------------------------------------------------------")
        return cleaned_data


class OptionalUserNameMixIn(ComputedFieldsMixIn):
    """If possible, creates a username according to rules (defaults to email then to name), otherwise set manually. """

    strict_username = True  # case_insensitive
    strict_email = False  # unique_email and case_insensitive

    class Meta:
        model = UserHC
        USERNAME_FLAG_FIELD = 'username_not_email'
        fields = ('first_name', 'last_name', model.get_email_field_name(), USERNAME_FLAG_FIELD, model.USERNAME_FIELD, )
        computed_fields = (model.USERNAME_FIELD, USERNAME_FLAG_FIELD, )
        # strict_username = True  # case_insensitive
        # strict_email = False  # unique_email and case_insensitive
        help_texts = {
            model.USERNAME_FIELD: _("Without a unique email, a username is needed. Use suggested or create one. "),
            model.get_email_field_name(): _("Used for confirmation and typically for login"),
        }

    def __init__(self, *args, **kwargs):
        print("======================= OptionalUserNameMixIn =================================")
        model = getattr(self._meta, 'model', None)
        required_attributes = ('USERNAME_FIELD', 'get_email_field_name', 'is_active')
        if not model or not all(hasattr(model, ea) for ea in required_attributes):
            for ea in required_attributes:
                print(f"{ea}: {hasattr(model, ea)}")
            err = "Missing features for user model. Try subclassing Django's AbstractBaseUser, AbstractUser, or User. "
            raise ImproperlyConfigured(_(err))
        strict_email = kwargs.pop('strict_email', getattr(self, 'strict_email', None))
        strict_username = kwargs.pop('strict_username', getattr(self, 'strict_username', None))
        validator_kwargs ={'strict_email': strict_email, 'strict_username': strict_username}
        kwargs['validator_kwargs'] = validator_kwargs
        if hasattr(self, 'assign_focus_field'):
            username_field_name = self._meta.model.USERNAME_FIELD
            if username_field_name in kwargs.get('data', {}):
                email_field_name = self._meta.model.get_email_field_name()
                kwargs['named_focus'] = email_field_name
        super().__init__(*args, **kwargs)
        print("--------------------- FINISH OptionalUserNameMixIn --------------------")

    def username_from_email_or_names(self, username_field_name=None, email_field_name=None):
        """ Initial username field value. Must be evaluated after dependent fields populate cleaned_data. """
        name_fields = ('first_name', 'last_name', )
        email_field_name = email_field_name or self._meta.model.get_email_field_name()
        username_field_name = username_field_name or self._meta.model.USERNAME_FIELD
        normalize = self._meta.model.normalize_username
        result_value = self.field_computed_from_fields(field_names=(email_field_name, ), normalize=normalize)
        lookup = {"{}__iexact".format(username_field_name): result_value}
        try:
            if not result_value or self._meta.model._default_manager.filter(**lookup).exists():
                result_value = self.field_computed_from_fields(field_names=name_fields, normalize=normalize)
        except Exception as e:
            print("Unable to query to lookup if this username exists. ")
            print(e)
        return result_value

    def compute_username(self):
        """ Determine a str value or callable returning one and set this in self.initial dict. """
        # print("=================== CustomRegistrationForm.compute_username ===========================")
        model = self._meta.model
        username_field_name = model.USERNAME_FIELD
        field = self.computed_fields[username_field_name]
        email_field_name = model.get_email_field_name()
        result_value = self.username_from_email_or_names(username_field_name, email_field_name)
        self.initial[username_field_name] = field.initial = result_value
        return field

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
        cleaned_data = super().clean()  # compute fields, return self.cleaned_data, sets unique validation boolean.
        username_field_name = self._meta.model.USERNAME_FIELD
        username_value = self.cleaned_data.get(username_field_name, '')
        email_field_name = self._meta.model.get_email_field_name()
        email_value = self.cleaned_data.get(email_field_name, None)
        if username_field_name not in self.data and username_value != email_value:
            print("- - - - - - - - - Confirmation Required - - - - - - - - - - - - - - -")
            marked_safe_translatable_html = self.configure_username_confirmation()
            # print("---------------------- Form Data --------------------------------------")
            # for key, items in self.data.lists():
            #     print(f"{key}: {items} ")
            raise ValidationError(marked_safe_translatable_html)
        else:
            # print(" Computed Fields had no problems! ")
            self.fields.update(self.computed_fields)
        error_dict = self.handle_flag_field(email_field_name, username_field_name)
        if error_dict:
            print("We had an error processing the flag. ")
            raise ValidationError(error_dict)
        return cleaned_data


class FormOverrideMixIn:

    prep_modifiers = None
    alt_field_info = {}
    formfield_attrs_overrides = {
        '_default_': {'size': 15, },
        'email': {'maxlength': 191, 'size': 20, },
        'billing_country_area': {'maxlength': 2, 'size': 2, },
        'billing_postcode': {'maxlength': 5, 'size': 5, },
        }

    def __init__(self, *args, **kwargs):
        print("======================= FormOverrideMixIn.__init__ =================================")
        super().__init__(*args, **kwargs)
        self.fields = self.prep_fields()
        print("--------------------- FINISH FormOverrideMixIn.__init__ --------------------")

    def set_alt_data(self, data=None, name='', field=None, value=None):
        """ Modify the form submitted value if it matches a no longer accurate default value. """
        # print("======================== set_alt_data ==================================")
        if not data:
            data = {name: (field, value, )}
        new_data = {}
        for name, field_val in data.items():
            field, value = field_val
            initial = self.get_initial_for_field(field, name)
            data_name = self.add_prefix(name)
            data_val = field.widget.value_from_datadict(self.data, self.files, data_name)
            if not field.has_changed(initial, data_val):
                self.initial[name] = value  # TODO: Won't work since initial determined earlier.
                new_data[data_name] = value
        if new_data:
            data = self.data.copy()
            data.update(new_data)
            data._mutable = False
            self.data = data

    def get_alt_field_info(self):
        """ Checks conditions for each key in alt_field_info. Returns a dict of field names and attribute overrides. """
        initial_field_info = getattr(self, 'alt_field_info', None)
        if not initial_field_info:
            return {}
        result = {}
        for key, field_info in initial_field_info.items():
            method_name = 'condition_' + key  # calls methods like condition_alt_country, etc.
            is_condition = getattr(self, method_name)() if hasattr(self, method_name) else False
            if is_condition:
                result.update(field_info)
        return result

    def get_flat_fields_setting(self):
        flat_fields = getattr(self, 'flat_fields', True)
        flat_fields = False if hasattr(self, 'fieldsets') or hasattr(self, '_fieldsets') else flat_fields
        self.flat_fields = flat_fields
        return flat_fields

    def handle_modifiers(self, opts, *args, **kwargs):
        """ The parameters are passed to methods whose names are in a list assigned to modifiers for this fieldset. """
        modifiers = (getattr(self, mod) for mod in opts.get('modifiers', []) if hasattr(self, mod))
        for mod in modifiers:
            opts, *args, kwargs = mod(opts, *args, **kwargs)
        return (opts, *args, kwargs)

    def prep_fields(self, *prep_args, **kwargs):
        """ Returns a copy after it modifies self.fields according to overrides, country switch, and maxlength. """
        fields = self.fields
        if self.get_flat_fields_setting():  # collect and apply all prep methods
            print("Not fieldsets. ")
            opts = {'modifiers': getattr(self, 'prep_modifiers', None) or []}
            args = [opts, None, fields, prep_args]
            kwargs.update(flat_fields=True)
            opts, _skipped, fields, *prep_args, kwargs = self.handle_modifiers(*args, **kwargs)
        overrides = getattr(self, 'formfield_attrs_overrides', {})
        DEFAULT = overrides.get('_default_', {})
        alt_field_info = self.get_alt_field_info()  # condition_<label> methods may modify self.fields
        new_data = {}
        for name, field in fields.items():
            if name in overrides:
                field.widget.attrs.update(overrides[name])
            if not overrides.get(name, {}).get('no_size_override', False):
                # TODO: Correct size attributes for all form controls: textarea, others?
                default = DEFAULT.get('size', None)  # Cannot use float("inf") as an int.
                display_size = field.widget.attrs.get('size', None)
                input_size = field.widget.attrs.get('maxlength', None)
                if input_size:
                    possible_size = [int(ea) for ea in (display_size or default, input_size) if ea]
                    # field.widget.attrs['size'] = str(int(min(float(display_size), float(input_size))))
                    field.widget.attrs['size'] = str(min(possible_size))
            if name in alt_field_info:
                for prop, value in alt_field_info[name].items():
                    if prop == 'initial' or prop == 'default':
                        new_data[name] = (field, value, )
                    setattr(field, prop, value)
        if new_data:
            self.set_alt_data(new_data)
        return fields


class OptionalCountryMixIn(FormOverrideMixIn):

    country_display = forms.CharField(widget=forms.HiddenInput(), initial='local', )
    other_country = forms.BooleanField(
        label=_("Not a {} address. ".format(settings.DEFAULT_COUNTRY)),
        required=False, )
    country_field_name = 'billing_country_code'
    other_country_switch = True
    prep_modifiers = ['prep_country_fields']
    alt_field_info = {
        'alt_country': {
            'billing_country_area': {
                    'label': _("Territory, or Province"),
                    'help_text': '',
                    'initial': '',
                    'default': '', },
            'billing_postcode': {
                    'label': _("Postal Code"),
                    'help_text': '', },
            'billing_country_code': {
                    # 'label': _(""),
                    'help_text': _("Here is your country field!"),
                    'default': '', },
            },
        }

    def __init__(self, *args, **kwargs):
        print("================= OptionalCountryMixIn(FormOverrideMixIn).__init__ ============================")
        name = self.country_field_name
        field = self.base_fields.get(name, None)
        default = settings.DEFAULT_COUNTRY
        display_ver = 'local'
        if self.other_country_switch and field:
            data = kwargs.get('data', {})
            if not data:  # Unbound form - initial display of the form.
                self.base_fields['country_display'] = self.country_display
                self.base_fields['other_country'] = self.other_country
                # print("Put 'country_display' and 'other_country' into base fields. ")
            else:  # The form has been submitted.
                display = data.get('country_display', 'DISPLAY NOT FOUND')
                other_country = data.get('other_country', None)
                val = data.get(name, None)
                if display == 'local' and other_country:  # self.country_display.initial
                    display_ver = 'foreign'
                    data = data.copy()
                    data['country_display'] = display_ver
                    if val == default:
                        data[name] = ''
                    data._mutable = False
                    kwargs['data'] = data
                log = f"Displayed {display}, country value {val}, with default {default}. "
                log += "Checked foreign country. " if other_country else "Not choosing foreign. "
                print(log)
            print("-------------------------------------------------------------")
        # else: Either this form does not have an address, or they don't what the switch functionality.
        print(display_ver)
        super().__init__(*args, **kwargs)
        print("------------- FINISH OptionalCountryMixIn(FormOverrideMixIn).__init__ FINISH ------------------")

    def condition_alt_country(self):
        """ Returns a boolean if the alt_field_info['alt_country'] field info should be applied. """
        alt_country = False
        if self.other_country_switch:
            alt_country = self.data.get('other_country', False)
            if not alt_country:
                self.fields.pop(self.country_field_name, None)
        return bool(alt_country)

    def prep_country_fields(self, opts, field_rows, remaining_fields, *args, **kwargs):
        """ Used in make_fieldsets for a row that has the country field (if present) and the country switch. """
        print("==================== OptionalCountryMixIn.prep_country_fields ==========================")
        if not self.other_country_switch:
            return (opts, field_rows, remaining_fields, *args, kwargs)
        field_rows = field_rows or []
        field_name = self.country_field_name
        field = remaining_fields.pop(field_name, None)
        result = {field_name: field} if field else {}
        other_country_field = remaining_fields.pop('other_country', None)
        if not other_country_field:
            other_country_field = self.base_fields['other_country'].copy()
            # country_name = settings.DEFAULT_COUNTRY
            # label = "Not a {} address. ".format(country_name)
            # other_country_field = forms.BooleanField(label=_(label), required=False, )
            # self.fields['other_country'] = other_country_field
        result.update({'other_country': other_country_field})
        attempted_field_names = ('other_country', self.country_field_name, )
        if result:
            field_rows.append(result)
        if kwargs.get('flat_fields', None) is True:
            remaining_fields.update(result)
        else:
            opts['fields'].append(attempted_field_names)
        return (opts, field_rows, remaining_fields, *args, kwargs)

    def clean_other_country(self):
        print("================== Clean Other Country ================================")
        other_country = self.cleaned_data.get('other_country', None)  # TODO: appropriate default?
        if other_country:
            field = self.fields.get(self.country_field_name, None)
            print(self.country_field_name)
            print(field.initial)
            print(self.data.get(self.country_field_name, None))
            raise forms.ValidationError("You can input your address. ")
        return other_country


class FormFieldSetMixIn(FormOverrideMixIn):
    """ Forms can be defined with multiple fields within the same row. Allows fieldsets in all as_<type> methods. """

    fieldsets = (
        (None, {
            'position': 1,
            'fields': [('first_name', 'last_name', )],
        }),
        (_('username'), {
            'classes': ('noline', ),
            'position': None,
            'fields': ['username'],
        }),
        (_('address'), {
            'classes': ('collapse', 'address', ),
            'modifiers': ['address', 'prep_country_fields', ],
            'position': 'end',
            'fields': [
                'billing_address_1',
                'billing_address_2',
                ('billing_city', 'billing_country_area', 'billing_postcode', )
                ],
        }), )
    max_label_width = 12
    label_width_widgets = (Input, Textarea, )  # Base classes for the field.widgets we want.
    label_exclude_widgets = (CheckboxInput, HiddenInput)  # classes for the field.widgets we do NOT want.
    # ignored_base_widgets = ['ChoiceWidget', 'MultiWidget', 'SelectDateWidget', ]
    # 'ChoiceWidget' is the base for 'RadioSelect', 'Select', and variations.

    def __init__(self, *args, **kwargs):
        print("======================= FormFieldSetMixIn.__init__ =================================")
        super().__init__(*args, **kwargs)
        self._fieldsets = self.make_fieldsets()
        print("--------------------- FINISH FormFieldSetMixIn.__init__ --------------------")

    def prep_remaining(self, opts, field_rows, remaining_fields, *args, **kwargs):
        """ This can be updated for any additional processing of fields not in any other fieldsets. """
        print("========================= FormFieldSetMixIn.prep_remaining ==================================")
        return (opts, field_rows, remaining_fields, *args, kwargs)

    def make_fieldsets(self, *fs_args, **kwargs):
        """ Updates the dictionaries of each fieldset with 'rows' of field dicts, and a flattend 'field_names' list. """
        print("======================= FormFieldSetMixIn.make_fieldsets =================================")
        remaining_fields = self.fields.copy()
        fieldsets = list(getattr(self, 'fieldsets', ((None, {'fields': [], 'position': None}), )))
        assigned_field_names = flatten([flatten(opts['fields']) for fieldset_label, opts in fieldsets])
        unassigned_field_names = [name for name in remaining_fields if name not in assigned_field_names]
        opts = {'modifiers': 'prep_remaining', 'position': 'remaining', 'fields': unassigned_field_names}
        fieldsets.append((None, opts))  # TODO: Check for issues tracking if any other added or removed fields.
        top_errors = self.non_field_errors().copy()
        max_position, form_column_count, hidden_fields, remove_idx = 0, 0, [], []
        for index, fieldset in enumerate(fieldsets):
            fieldset_label, opts = fieldset
            if 'fields' not in opts or 'position' not in opts:
                raise ImproperlyConfigured(_("There must be 'fields' and 'position' in each fieldset. "))
            field_rows = []
            for ea in opts['fields']:
                row = [ea] if isinstance(ea, str) else ea
                existing_fields = {}
                for name in row:
                    if name not in remaining_fields:
                        # Okay when a fieldset defines field names not present in current form.
                        # so if a field name is in remaining fieldset, but already used, skip it.
                        continue
                    field = remaining_fields.pop(name)
                    bf = self[name]
                    bf_errors = self.error_class(bf.errors)
                    if bf.is_hidden:
                        if bf_errors:
                            top_errors.extend(
                                [_('(Hidden field %(name)s) %(error)s') %
                                    {'name': name, 'error': str(e)}
                                    for e in bf_errors])
                        hidden_fields.append(str(bf))
                    else:
                        existing_fields[name] = field
                if existing_fields:  # only adding non-empty rows. May be empty if these fields are not in current form.
                    field_rows.append(existing_fields)
            if field_rows:
                args = [opts, field_rows, remaining_fields, *fs_args]
                opts, field_rows, remaining_fields, *fs_args, kwargs = self.handle_modifiers(*args, **kwargs)
                fs_column_count = max(len(row) for row in field_rows)
                opts['field_names'] = flatten(opts['fields'])
                opts['rows'] = field_rows
                opts['column_count'] = fs_column_count
                if fieldset_label is None:
                    form_column_count = max((fs_column_count, form_column_count))
                max_position += 1
            else:
                remove_idx.append(index)
        for index in reversed(remove_idx):
            fieldsets.pop(index)
        max_position += 1
        if len(remaining_fields):
            pprint(remaining_fields)
            raise ImproperlyConfigured(_("Some unassigned fields, perhaps some added during make_fieldset. "))
        lookup = {'end': max_position + 2, 'remaining': max_position + 1, None: max_position}
        fieldsets = [(k, v) for k, v in sorted(fieldsets,
                     key=lambda ea: lookup.get(ea[1]['position'], ea[1]['position']))
                     ]
        summary = {'top_errors': top_errors, 'hidden_fields': hidden_fields, 'columns': form_column_count}
        self._fieldsets = fieldsets.copy()
        self._fs_summary = summary
        fieldsets.append(('summary', summary, ))
        return fieldsets

    def determine_label_width(self, field_rows):
        """ Returns a attr_dict and list of names of fields whose labels should apply these attributes. """
        visual_group, styled_labels, label_attrs_dict = [], [], {}
        if len(self.label_width_widgets) < 1:
            return label_attrs_dict, styled_labels
        single_field_rows = [row for row in field_rows if len(row) == 1]
        if len(single_field_rows) > 1:
            for field_dict in single_field_rows:
                name = list(field_dict.keys())[0]
                field = list(field_dict.values())[0]
                klass = field.widget.__class__
                if issubclass(klass, self.label_width_widgets) and \
                   not issubclass(klass, getattr(self, 'label_exclude_widgets', [])) and \
                   getattr(field, 'label', None):
                    visual_group.append((name, field, ))
        if len(visual_group) > 1:
            max_label_length = max(len(field.label) for name, field in visual_group)
            width = (max_label_length + 1) // 2  # * 0.85 ch
            if width > self.max_label_width:
                max_word_length = max(len(w) for name, field in visual_group for w in field.label.split())
                width = max_word_length // 2
            style_text = 'width: {}rem; display: inline-block'.format(width)
            label_attrs_dict = {'style': style_text}
            styled_labels = [name for name, field in visual_group]
        return label_attrs_dict, styled_labels

    def _html_tag(self, tag, contents, attr_string=''):
        """Wraps 'contents' in an HTML element with an open and closed 'tag', applying the 'attr_string' attributes. """
        return '<' + tag + attr_string + '>' + contents + '</' + tag + '>'

    def column_formats(self, col_head_tag, col_tag, single_col_tag, col_head_data, col_data):
        """ Returns multi-column and single-column string formatters with head and nested tags as needed. """
        col_html, single_col_html = '', ''
        attrs = '%(html_col_attr)s'
        if col_head_tag:
            col_html += self._html_tag(col_head_tag, col_head_data, '%(html_head_attr)s')
            single_col_html += col_html
        col_html += self._html_tag(col_tag, col_data, attrs)
        single_col_html += col_data if not single_col_tag else self._html_tag(single_col_tag, col_data, attrs)
        return col_html, single_col_html

    def make_row(self, columns_data, error_data, row_tag, html_row_attr=''):
        """ Flattens data lists, wraps them in HTML element of provided tag and attr string. Returns a list. """
        result = []
        if error_data:
            row = self._html_tag(row_tag, ' '.join(error_data))
            result.append(row)
        if columns_data:
            row = self._html_tag(row_tag, ' '.join(columns_data), html_row_attr)
            result.append(row)
        return result

    def make_headless_row(self, html_args, html_el, column_count, col_attr='', row_attr=''):
        """ Creates a row with no column head, spaned across as needed. Used for top errors and imbedding fieldsets. """
        row_tag, col_head_tag, col_tag, single_col_tag, as_type, all_fieldsets = html_args
        if as_type == 'table' and column_count > 0:
            colspan = column_count * 2 if col_head_tag else column_count
            col_attr += f' colspan="{colspan}"' if colspan > 1 else ''
        if single_col_tag:
            html_el = self._html_tag(single_col_tag, html_el, col_attr)
        else:
            row_attr += col_attr
        html_el = self._html_tag(row_tag, html_el, row_attr)
        return html_el

    def form_main_rows(self, html_args, fieldsets, form_col_count):
        """ Returns a list of formatted content of each main form 'row'. Called after preparing fields and row_data. """
        *args, as_type, all_fieldsets = html_args
        output = []
        for fieldset_label, opts in fieldsets:
            row_data = opts['row_data']
            if all_fieldsets or fieldset_label is not None:
                container_attr = f' class="fieldset_{as_type}""'
                container = None if as_type in ('p', 'fieldset') else as_type
                data = '\n'.join(row_data)
                if container:
                    data = self._html_tag(container, data, container_attr) + '\n'
                if fieldset_label:
                    legend = self._html_tag('legend', fieldset_label) + '\n'
                    fieldset_attr = ''
                else:
                    legend = ''
                    fieldset_attr = ' class="noline"'
                fieldset_el = self._html_tag('fieldset', legend + data, fieldset_attr)
                if container:
                    col_attr = ''
                    row_attr = ' class="fieldset_row"'
                    fieldset_el = self.make_headless_row(html_args, fieldset_el, form_col_count, col_attr, row_attr)
                output.append(fieldset_el)
            else:
                output.extend(row_data)
        return output

    def _html_output(self, row_tag, col_head_tag, col_tag, single_col_tag, col_head_data, col_data,
                     help_text_br, errors_on_separate_row, as_type=None, strict_columns=False):
        """ Overriding BaseForm._html_output. Output HTML. Used by as_table(), as_ul(), as_p(), etc. """
        help_tag = 'span'
        allow_colspan = not strict_columns and as_type == 'table'
        adjust_label_width = getattr(self, 'adjust_label_width', True)
        if as_type == 'table':
            label_width_attrs_dict, width_labels = {}, []
            adjust_label_width = False
        all_fieldsets = True if as_type == 'fieldset' else False
        html_args = [row_tag, col_head_tag, col_tag, single_col_tag, as_type, all_fieldsets]
        col_html, single_col_html = self.column_formats(col_head_tag, col_tag, single_col_tag, col_head_data, col_data)
        fieldsets = getattr(self, '_fieldsets', None) or self.make_fieldsets()
        summary = getattr(self, '_fs_summary', None)
        if fieldsets[-1][0] == 'summary':
            summary = fieldsets.pop()[1]
        data_labels = ('top_errors', 'hidden_fields', 'columns')
        assert isinstance(summary, dict) and all(ea in summary for ea in data_labels), "Malformed fieldsets summary. "
        form_col_count = 1 if all_fieldsets else summary['columns']
        col_double = col_head_tag and as_type == 'table'

        for fieldset_label, opts in fieldsets:
            if adjust_label_width:
                label_width_attrs_dict, width_labels = self.determine_label_width(opts['rows'])
            col_count = opts['column_count'] if fieldset_label else form_col_count
            row_data = []
            for row in opts['rows']:
                multi_field_row = False if len(row) == 1 else True
                columns_data, error_data, html_row_attr = [], [], ''
                for name, field in row.items():
                    field_attrs_dict = {}
                    bf = self[name]
                    bf_errors = self.error_class(bf.errors)
                    if errors_on_separate_row and bf_errors:
                        colspan = 1 if multi_field_row else col_count
                        colspan *= 2 if col_double else 1
                        attr = ''
                        if colspan > 1 and allow_colspan:
                            attr += ' colspan="{}"'.format(colspan)
                        tag = col_tag if multi_field_row else single_col_tag
                        err = str(bf_errors) if not tag else self._html_tag(tag, bf_errors, attr)
                        error_data.append(err)
                    css_classes = bf.css_classes()  # a string of space seperated css classes.
                    # can add to css_classes, used to make 'class="..."' attribute if the row or column should need it.
                    if multi_field_row:
                        css_classes = ' '.join(['nowrap', css_classes])
                    if bf.label:
                        attrs = label_width_attrs_dict if name in width_labels else {}
                        label = conditional_escape(bf.label)
                        label = bf.label_tag(label, attrs) or ''
                    else:  # TODO: Check bf.label always exists?
                        raise ImproperlyConfigured(_("Visible Bound Fields must have a non-empty label. "))
                    if field.help_text:
                        help_text = '<br />' if help_text_br else ''
                        help_text += str(field.help_text)
                        id_ = field.widget.attrs.get('id') or bf.auto_id
                        field_html_id = field.widget.id_for_label(id_) if id_ else ''
                        help_id = field_html_id or bf.html_name
                        help_id += '-help'
                        field_attrs_dict.update({'aria-describedby': help_id})
                        help_attr = ' id="{}" class="help-text"'.format(help_id)
                        help_text = self._html_tag(help_tag, help_text, help_attr)
                    else:
                        help_text = ''
                    html_class_attr = ' class="%s"' % css_classes if css_classes else ''
                    html_row_attr = ''
                    html_head_attr = ' class="nowrap"' if multi_field_row else ''
                    html_col_attr = html_class_attr
                    if allow_colspan and not multi_field_row and col_count > 1:
                        colspan = col_count * 2 - 1 if col_double else col_count
                        html_col_attr += ' colspan="{}"'.format(colspan)
                    if field_attrs_dict:
                        field_display = bf.as_widget(attrs=field_attrs_dict)
                        if field.show_hidden_initial:
                            field_display += bf.as_hidden(only_initial=True)
                    else:
                        field_display = bf
                    format_kwargs = {
                        'errors': bf_errors,
                        'label': label,
                        'field': field_display,
                        'help_text': help_text,
                        'html_head_attr': html_head_attr,
                        'html_col_attr': html_col_attr,
                        'field_name': bf.html_name,
                    }
                    if multi_field_row:
                        columns_data.append(col_html % format_kwargs)
                    else:
                        columns_data.append(single_col_html % format_kwargs)
                        if not col_head_tag and not single_col_tag:
                            html_row_attr += html_col_attr
                row_data.extend(self.make_row(columns_data, error_data, row_tag, html_row_attr))
            # end iterating field rows
            opts['row_data'] = row_data
        # end iterating fieldsets
        output = []
        top_errors = summary['top_errors']
        if top_errors:
            col_attr = ' id="top_errors"'
            row_attr = ''
            data = ' '.join(top_errors)
            error_row = self.make_headless_row(html_args, data, form_col_count, col_attr, row_attr)
            output.append(error_row)
        output.extend(self.form_main_rows(html_args, fieldsets, form_col_count))
        hidden_fields = summary['hidden_fields']
        if hidden_fields:  # Insert any hidden fields in the last row.
            str_hidden = ''.join(hidden_fields)
            if output:
                last_row = output[-1]
                # Chop off the trailing row_ender (e.g. '</td></tr>') and insert the hidden fields.
                row_ender = '' if not single_col_tag else '</' + single_col_tag + '>'
                row_ender += '</' + row_tag + '>'
                if last_row.endswith(row_ender):
                    output[-1] = last_row[:-len(row_ender)] + str_hidden + row_ender
                else:
                    # This can happen in the as_p() case (and possibly other custom display methods).
                    # If there are only top errors, we may not be able to conscript the last row for
                    # our purposes, so insert a new empty row.
                    col_attr = ''
                    row_attr = ''
                    last_row = self.make_headless_row(html_args, str_hidden, form_col_count, col_attr, row_attr)
                    output.append(last_row)
            else:  # If there aren't any rows in the output, just append the hidden fields.
                output.append(str_hidden)
        return mark_safe('\n'.join(output))

    def as_table(self):
        "Overwrite BaseForm.as_table. Return this form rendered as HTML <tr>s -- excluding the <table></table>."
        return self._html_output(
            row_tag='tr',
            col_head_tag='th',
            col_tag='td',
            single_col_tag='td',
            col_head_data='%(label)s',
            col_data='%(errors)s%(field)s%(help_text)s',
            help_text_br=True,
            errors_on_separate_row=False,
            as_type='table',
            strict_columns=False,
        )

    def as_ul(self):
        "Overwrite BaseForm.as_ul. Return this form rendered as HTML <li>s -- excluding the <ul></ul>."
        return self._html_output(
            row_tag='li',
            col_head_tag=None,
            col_tag='span',
            single_col_tag='',
            col_head_data='',
            col_data='%(errors)s%(label)s%(field)s%(help_text)s',
            help_text_br=False,
            errors_on_separate_row=False,
            as_type='ul',
        )

    def as_p(self):
        "Overwrite BaseForm.as_p. Return this form rendered as HTML <p>s."
        return self._html_output(
            row_tag='p',
            col_head_tag=None,
            col_tag='span',
            single_col_tag='',
            col_head_data='',
            col_data='%(label)s%(field)s%(help_text)s',
            help_text_br=False,
            errors_on_separate_row=True,
            as_type='p'
        )

    def as_fieldset(self):
        " Return this form rendered as, or in, HTML <fieldset>s. Untitled fieldsets will be borderless. "
        return self._html_output(
            row_tag='p',
            col_head_tag=None,
            col_tag='span',
            single_col_tag='',
            col_head_data='',
            col_data='%(errors)s%(label)s%(field)s%(help_text)s',
            help_text_br=False,
            errors_on_separate_row=False,
            as_type='fieldset',
        )


class PersonFormMixIn(FocusMixMin, FormFieldSetMixIn, OptionalCountryMixIn):  # FormFieldSetMixIn,
    """ Using fieldsets, optional country & username (with override and computed fields) and focus. """
    # TODO: Determine correct import order

    def as_test(self):
        """ Prepares and calls different 'as_<variation>' method variations. """
        container = 'ul'  # table, ul, p, fieldset, ...
        func = getattr(self, 'as_' + container)
        display_data = func()
        if container not in ('p', 'fieldset', ):
            display_data = self._html_tag(container, display_data)
        return mark_safe(display_data)

    def test_field_order(self, data):
        """ Deprecated. Log printing the dict, array, or tuple in the order they are currently stored. """
        log_lines = [(key, value) for key, value in data.items()] if isinstance(data, dict) else data
        for line in log_lines:
            pprint(line)

    def _html_tag(self, tag, contents, attr_string=''):
        """Wraps 'contents' in an HTML element with an open and closed 'tag', applying the 'attr_string' attributes. """
        return '<' + tag + attr_string + '>' + contents + '</' + tag + '>'

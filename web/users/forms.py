from django import forms
from django.utils.translation import gettext as _
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django_registration.forms import RegistrationForm
from django_registration import validators
from pprint import pprint  # TODO: Remove after debug.USERNAME_FLAG_FIELD
from .models import UserHC
from .mixins import PersonFormMixIn, ExtractFieldsMixIn


class CustomRegistrationForm(PersonFormMixIn, ExtractFieldsMixIn, RegistrationForm):

    tos = forms.BooleanField(
        widget=forms.CheckboxInput,
        label=_("I have read and agree to the Terms of Service"),
        error_messages={"required": validators.TOS_REQUIRED}, )
    tos_required = False

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
        print("================================== CustomRegistrationForm.__init__ =====================")
        if self.tos_required:
            self.base_fields['tos'] = self.tos
        kwargs['computed_fields'] = self.Meta.computed_fields
        kwargs['strict_email'] = self.Meta.strict_email
        kwargs['strict_username'] = self.Meta.strict_username
        super().__init__(*args, **kwargs)
        # TODO: If using RegistrationForm init, then much, but not all, of attach_critical_validators is duplicate code.
        print("--------------------- FINISH users.CustomRegistrationForm.__init__ --------------------")


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

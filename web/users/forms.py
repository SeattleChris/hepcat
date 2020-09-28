from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext as _
from django_registration.forms import RegistrationForm
from django_registration import validators
from .models import UserHC
from .mixins import AddressMixIn, AddressUsernameMixIn


class CustomRegistrationForm(AddressUsernameMixIn, RegistrationForm):

    tos = forms.BooleanField(
        widget=forms.CheckboxInput,
        label=_("I have read and agree to the Terms of Service"),
        error_messages={"required": validators.TOS_REQUIRED}, )
    tos_required = False
    USERNAME_FLAG_FIELD = 'username_not_email'

    class Meta(RegistrationForm.Meta):
        model = UserHC
        fields = ('first_name', 'last_name', model.get_email_field_name(), model.USERNAME_FIELD, )
        # computed_fields = []  # The computed fields needed for username and address will be added.
        help_texts = {
            model.USERNAME_FIELD: _("Without a unique email, a username is needed. Use suggested or create one. "),
            model.get_email_field_name(): _("Used for confirmation and typically for login"),
        }

    def __init__(self, *args, **kwargs):
        print("================================== CustomRegistrationForm.__init__ =====================")
        if not self.tos_required:
            self.base_fields.pop('tos', None)
        super().__init__(*args, **kwargs)
        # TODO: If using RegistrationForm init, then much, but not all, of attach_critical_validators is duplicate code.
        print("--------------------- FINISH users.CustomRegistrationForm.__init__ --------------------")


class CustomUserCreationForm(UserCreationForm):
    """ Deprecated, prefer CustomRegistrationForm. This will be removed after feature and integration are confirmed. """
    class Meta(UserCreationForm.Meta):
        model = UserHC
        fields = ('first_name', 'last_name', 'email')  # 'username_not_email',


class CustomUserChangeForm(AddressMixIn, UserChangeForm):
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

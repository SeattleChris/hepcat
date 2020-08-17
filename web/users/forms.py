# from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import UserHC


class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = UserHC
        fields = ('first_name', 'last_name', 'uses_email_username', 'email')
        # fields = ('first_name', 'last_name', 'uses_email_username', 'username', 'email', 'is_student', 'is_teacher', 'is_admin')
        # fields = ('username', 'email')


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

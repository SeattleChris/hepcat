# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import UserHC


class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = UserHC
        fields = ('first_name', 'last_name', 'username', 'email')


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = UserHC
        fields = ('first_name', 'last_name', 'username', 'email')

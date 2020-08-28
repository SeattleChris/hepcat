from django.urls import path, include
# from django.views.generic.base import RedirectView
from django.contrib.auth.views import PasswordChangeView
# from django.contrib.auth.views import LoginView
# from django.contrib.auth.forms import AuthenticationForm
from .views import CustomRegistrationView, Modify  # , SignUp,
# TODO: Report that the UserChangeForm seems to have a hard coded a element href attribute of '../password/'
# TODO: Submit a PR to django-registration for docs update to include One-step workflow URL names.

urlpatterns = [
    # Should have either one-step or two-step workflow setup with the following:
    path('register/', CustomRegistrationView.as_view(), name='signup'),  # One-step, customized.
    path('', include('django_registration.backends.one_step.urls')),  # One-step, defaults and/or remaining views.
    # path('user/', include('django_registration.backends.activation.urls')),  # for two-step activation workflow
    # path('signup/', SignUp.as_view(), name='signup'),  # Technique not using django-registration.
    path('update/', Modify.as_view(), name='user_update'),
    path('password/', PasswordChangeView.as_view(template_name='update.html'), name='password'),
]

# One-step workflow defines the following URL names (django_registration.backends.one_step.urls):
# django_registration_register is the account-registration view.
# django_registration_disallowed is a message indicating registration is not currently permitted.
# django_registration_complete is the post-registration success message.

# Two-step workflow defines the following URL names (django_registration.backends.activation.urls):
# django_registration_register is the account-registration view.
# django_registration_complete is the post-registration success message.
# django_registration_activate is the account-activation view.
# django_registration_activation_complete is the post-activation success message.
# django_registration_disallowed is a message indicating registration is not currently permitted.

# Thanks to django.contrib.auth.urls The following paths are set (in hepcat.urls):
# user/login/ [name='login']
# user/logout/ [name='logout']
# user/password_change/ [name='password_change']
# user/password_change/done/ [name='password_change_done']
# user/password_reset/ [name='password_reset']
# user/password_reset/done/ [name='password_reset_done']
# user/reset/<uidb64>/<token>/ [name='password_reset_confirm']
# user/reset/done/ [name='password_reset_complete']

from django.urls import path
# from django.views.generic.base import RedirectView
from django.contrib.auth.views import PasswordChangeView
from django_registration.backends.one_step.views import RegistrationView
from .views import SignUp, Modify
from .forms import CustomUserCreationForm
# TODO: Report that the UserChangeForm seems to have a hard coded a element href attribute of '../password/'

urlpatterns = [
    # TODO: Set a registration page from one of the following:
    path('register/',
         RegistrationView.as_view(
             success_url='/profile/',
             form_class=CustomUserCreationForm,
         ),
         name='django_registration_register'),
    # path('user/', include('django_registration.backends.activation.urls')),
    # path('user/', include('django_registration.backends.one_step.urls')),
    path('signup/', SignUp.as_view(), name='signup'),
    path('update/', Modify.as_view(), name='user_update'),
    path('password/', PasswordChangeView.as_view(template_name='update.html'), name='password'),
]

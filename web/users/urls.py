from django.urls import path, include
# from django.views.generic.base import RedirectView
from django.contrib.auth.views import PasswordChangeView
from .views import CustomRegistrationView, SignUp, Modify
# TODO: Report that the UserChangeForm seems to have a hard coded a element href attribute of '../password/'

urlpatterns = [
    # TODO: Set a registration page from one of the following:
    # path('user/', include('django_registration.backends.activation.urls')),  # for two-step activation workflow
    path('', include('django_registration.backends.one_step.urls')),
    path('register/', CustomRegistrationView.as_view(), name='django_registration_register'),
    path('signup/', SignUp.as_view(), name='signup'),
    path('update/', Modify.as_view(), name='user_update'),
    path('password/', PasswordChangeView.as_view(template_name='update.html'), name='password'),
]

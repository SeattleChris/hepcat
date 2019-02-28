"""hepcat URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
# from django_registration.backends.one_step import RegistrationView
from .views import home_view


urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    # path('user/', include('django_registration.backends.activation.urls')),
    # path('user/register/', include('django_registration.backends.one_step.urls')),
    # path('user/register/',
    #      RegistrationView.as_view(success_url='/profile/'),
    #      name='django_registration_register'),
    path('user/', include('django.contrib.auth.urls')),
    path('user/', include('users.urls')),
    path('classes/', include('classwork.urls')),
    # path('payments/', include('payments.urls')),
]

# Thanks to django.contrib.auth.urls The following paths are set:
# user/login/ [name='login']
# user/logout/ [name='logout']
# user/password_change/ [name='password_change']
# user/password_change/done/ [name='password_change_done']
# user/password_reset/ [name='password_reset']
# user/password_reset/done/ [name='password_reset_done']
# user/reset/<uidb64>/<token>/ [name='password_reset_confirm']
# user/reset/done/ [name='password_reset_complete']

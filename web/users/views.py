from django.urls import reverse_lazy
from django.views import generic
from .models import UserHC
# from django_registration.views import RegistrationView as BaseRegistrationView
from django_registration.backends.one_step.views import RegistrationView
from .forms import CustomRegistrationForm, CustomUserCreationForm, CustomUserChangeForm
# from django.contrib.auth.forms import UserCreationForm, UserChangeForm
# Create your views here.


class CustomRegistrationView(RegistrationView):
    form_class = CustomRegistrationForm
    success_url = reverse_lazy('profile_page')


class SignUp(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('profile_page')
    template_name = 'signup.html'


class Modify(generic.UpdateView):
    model = UserHC
    form_class = CustomUserChangeForm
    success_url = reverse_lazy('profile_page')
    template_name = 'update.html'

    def get_object(self, queryset=None):
        return self.request.user

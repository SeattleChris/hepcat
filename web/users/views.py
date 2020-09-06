from django.urls import reverse_lazy
from django.views import generic
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from .models import UserHC
# from django_registration.views import RegistrationView as BaseRegistrationView
from django_registration.backends.one_step.views import RegistrationView
from .forms import CustomRegistrationForm, CustomUserCreationForm, CustomUserChangeForm
from pprint import pprint  # TODO: Remove after debug

# Create your views here.


@method_decorator(csrf_protect, name='dispatch')
class CustomRegistrationView(RegistrationView):
    form_class = CustomRegistrationForm
    success_url = reverse_lazy('profile_page')

    def register(self, form):
        print("===================== CustomRegistrationView.register ============================")
        pprint(form)
        print("----------------------------------------------------------------------------------")
        pprint(self)
        return super().register(form)


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

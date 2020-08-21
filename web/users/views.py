from django.urls import reverse_lazy
from django.views import generic
from .models import UserHC
from .forms import CustomUserCreationForm, CustomUserChangeForm
# from django.contrib.auth.forms import UserCreationForm, UserChangeForm
# Create your views here.


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

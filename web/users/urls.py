from django.urls import path
# from django.views.generic.base import RedirectView
# from django.urls import reverse_lazy
from .views import SignUp, Modify  # , PasswordChange
from django.contrib.auth.views import PasswordChangeView

urlpatterns = [
    path('signup/', SignUp.as_view(), name='signup'),
    path('update/', Modify.as_view(), name='user_update'),
    path('password/', PasswordChangeView.as_view(template_name='update.html'), name='password'),
]

from django.urls import path
# from django.views.generic.base import RedirectView
# from django.urls import reverse_lazy
from .views import SignUp, Modify, PasswordChange

urlpatterns = [
    path('signup/', SignUp.as_view(), name='signup'),
    path('update/', Modify.as_view(), name='user_update'),
    path('password/', PasswordChange.as_view(), name='password'),
]

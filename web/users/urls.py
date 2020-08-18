from django.urls import path
from .views import SignUp, Modify

urlpatterns = [
    path('signup/', SignUp.as_view(), name='signup'),
    path('update/', Modify.as_view(), name='user_update'),
    # path('password/', Modify.as_view(), name='user_update'),
]

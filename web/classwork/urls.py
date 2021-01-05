from django.urls import path
from django.views.decorators.cache import cache_page
from .views import (AboutUsListView, ResourceDetailView,
                    ClassOfferDetailView, ClassOfferListView,
                    LocationDetailView, LocationListView,
                    Checkin, RegisterView, ProfileView,
                    PaymentProcessView, payment_details,
                    )
minute = 3  # Number of seconds in a minute.
# SubjectCreateView, SessionCreateView, ClassOfferCreateView,
urlpatterns = [  # All following are in root
     path('aboutus', AboutUsListView.as_view(), name='aboutus'),
     path('classes/<int:id>', ClassOfferDetailView.as_view(), name='classoffer_detail'),
     path('classes/', cache_page(minute * 15)(ClassOfferListView.as_view()), name='classoffer_list'),
     path('classes/sess/<str:display_session>', ClassOfferListView.as_view(), name='classoffer_display_session'),
     path('classes/date/<str:display_date>', ClassOfferListView.as_view(), name='classoffer_display_date'),
     path('location/<int:id>', LocationDetailView.as_view(), name='location_detail'),
     path('location/', LocationListView.as_view(), name='location_list'),
     path('checkin/<str:display_session>', Checkin.as_view(), name='checkin_session'),
     path('checkin/', Checkin.as_view(), name='checkin'),
     path('register/', RegisterView.as_view(), name='register'),
     path('payment/<int:id>', payment_details, name='payment'),
     path('payment/fail/<int:id>', PaymentProcessView.as_view(template_name='payment/fail.html'), name='payment_fail'),
     path('payment/success/<int:id>', PaymentProcessView.as_view(), name='payment_success'),
     path('payment/done/<int:id>', PaymentProcessView.as_view(template_name='payment/success.html'),
          name='payment_done'),
     path('student/<int:id>', ProfileView.as_view(profile_type='student'), name='profile_student'),
     path('staff/<int:id>', ProfileView.as_view(profile_type='staff'), name='profile_staff'),
     path('profile/<int:id>', ProfileView.as_view(), name='profile_user'),  # profile_type='profile'
     path('profile/', ProfileView.as_view(), name='profile_page'),
     path('resource/<int:id>', ResourceDetailView.as_view(), name='resource_detail'),
 ]

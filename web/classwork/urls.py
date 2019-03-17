from django.urls import path
from .views import (ClassOfferListView,
                    LocationDetailView, LocationListView,
                    RegisterView, PaymentProcessView, PaymentResultView,
                    Checkin, ProfileView, ResourceDetailView
                    )
# SubjectCreateView, SessionCreateView, ClassOfferCreateView,
urlpatterns = [  # All following are in root
    path('', ClassOfferListView.as_view(), name='classoffer_list'),  # Display all ClassOffers?
    path('location/<int:id>', LocationDetailView.as_view(), name='location_detail'),
    path('location/', LocationListView.as_view(), name='location_list'),
    path('checkin/', Checkin.as_view(), name='checkin'),
    path('register/', RegisterView.as_view(), name='register'),
    path('payment/', PaymentProcessView.as_view(), name='payment'),
    path('payment/fail/<int:id>', PaymentResultView.as_view(template_name='payment/fail.html'), name='payment_fail'),
    path('payment/done/<int:id>', PaymentResultView.as_view(template_name='payment/success.html'), name='payment_success'),
    path('profile/', ProfileView.as_view(), name='profile_page'),
    path('resource/<int:id>', ResourceDetailView.as_view(), name='resource_detail'),
 ]

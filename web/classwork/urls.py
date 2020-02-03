from django.urls import path
from .views import (AboutUsListView, ResourceDetailView,
                    ClassOfferDetailView, ClassOfferListView,
                    LocationDetailView, LocationListView,
                    Checkin, RegisterView, ProfileView,
                    PaymentProcessView, payment_details,
                    )
# SubjectCreateView, SessionCreateView, ClassOfferCreateView,
urlpatterns = [  # All following are in root
    path('aboutus', AboutUsListView.as_view(), name='aboutus'),
    path('classes/<int:id>', ClassOfferDetailView.as_view(), name='classoffer_detail'),
    path('classes/', ClassOfferListView.as_view(), name='classoffer_list'),
    path('location/<int:id>', LocationDetailView.as_view(), name='location_detail'),
    path('location/', LocationListView.as_view(), name='location_list'),
    path('checkin/', Checkin.as_view(), name='checkin'),
    path('register/', RegisterView.as_view(), name='register'),
    path('payment/<int:id>', payment_details, name='payment'),
    path('payment/fail/<int:id>', PaymentProcessView.as_view(template_name='payment/fail.html'), name='payment_fail'),
    path('payment/success/<int:id>', PaymentProcessView.as_view(), name='payment_success'),
    path('payment/done/<int:id>', PaymentProcessView.as_view(template_name='payment/success.html'), name='payment_done'),
    path('profile/', ProfileView.as_view(), name='profile_page'),
    path('resource/<int:id>', ResourceDetailView.as_view(), name='resource_detail'),
 ]

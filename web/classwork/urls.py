from django.urls import path
from .views import SubjectListView, SessionListView, ClassOfferListView, LocationDetailView, LocationListView
# SubjectCreateView, SessionCreateView, ClassOfferCreateView,
from .views import RegisterView, PaymentProcessView, PaymentResultView, Checkin, TableCheckin
urlpatterns = [  # All following are in /classes/
    path('', ClassOfferListView.as_view(), name='classoffer_list'),  # Display all ClassOffers?
    path('location/<int:id>', LocationDetailView.as_view(), name='location_detail'),
    path('location/', LocationListView.as_view(), name='location_list'),
    # path('new/', ClassOfferCreateView.as_view(), name='classoffer_create'),
    # path('<int:id>', ClassOfferDetailView.as_view(), name='classoffer_detail'),
    path('subject/', SubjectListView.as_view(), name='subject_list'),
    # path('subject/new/', SubjectCreateView.as_view(), name='subject_create'),
    path('session/', SessionListView.as_view(), name='session_list'),
    # path('session/new/', SessionCreateView.as_view(), name='session_create'),
    # path('classoffer/new/<int:id>', ClassOfferCreateView.as_view(), name='classoffer_create'),
    # above is correct to create on budget of id?
    path('checkin/', Checkin.as_view(), name='checkin'),
    path('table/', TableCheckin.as_view(), name='table'),
    path('register/', RegisterView.as_view(), name='register'),
    path('payment/', PaymentProcessView.as_view(), name='payment'),
    path('payment/fail/<int:id>', PaymentResultView.as_view(result='fail'), name='payment_fail'),
    path('payment/done/<int:id>', PaymentResultView.as_view(result='success'), name='payment_success'),
]

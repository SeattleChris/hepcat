from django.urls import path
from .views import SubjectListView, SubjectCreateView, SessionListView, SessionCreateView, ClassOfferListView, ClassOfferCreateView

urlpatterns = [
    # path('', PublishedListView.as_view(), name='published'),
    path('', ClassOfferListView.as_view(), name='classoffer_list'),
    path('new/', ClassOfferCreateView.as_view(), name='classoffer_create'),
    # path('<int:id>', ClassOfferDetailView.as_view(), name='classoffer_detail'),
    path('subject/', SubjectListView.as_view(), name='subject_list'),
    path('subject/new/', SubjectCreateView.as_view(), name='subject_create'),
    path('session/', SessionListView.as_view(), name='session_list'),
    path('session/new/', SessionCreateView.as_view(), name='session_create'),
    # path('classoffer/new/<int:id>', ClassOfferCreateView.as_view(), name='classoffer_create'),
    # above is correct to create on budget of id?
]

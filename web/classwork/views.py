from django.views.generic import ListView, CreateView
# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from .models import Subject, Session, ClassOffer
from .forms import SubjectForm, SessionForm, ClassOfferForm
# Create your views here.


# class PublishedListView(ListView):
#     """ Placeholder for currently live classes on the site
#     """
#     template_name = 'classwork/published.html'
#     model = ClassOffer
#     context_object_name = 'classoffers'


class SubjectListView(ListView):
    """ This will allow us to view a list of already made Subjects
    """
    template_name = 'classwork/subject_list.html'
    model = Subject
    context_object_name = 'subjects'


class SessionListView(ListView):
    """ This will allow us to view a list of sessions
    """
    template_name = 'classwork/session_list.html'
    model = Session
    context_object_name = 'sessions'


class SubjectCreateView(CreateView):
    """ This allows Subjects to be made
    """
    template_name = 'classwork/subject_create.html'
    model = Subject
    form_class = SubjectForm
    success_url = reverse_lazy('subject_list')
    # login_url = reverse_lazy('login')

    # def form_valid(self, form):
    #     """ Associate the privlidged user to this creation
    #     """
    #     form.instance.user = self.request.user
    #     return super().form_valid(form)

    # Inherits .as_view(self):


class SessionCreateView(CreateView):
    """ This allows sessions to be made
    """
    template_name = 'classwork/session_create.html'
    model = Session
    form_class = SessionForm
    success_url = reverse_lazy('session_list')
    # login_url = reverse_lazy('login')

    # def form_valid(self, form):
    #     """ Associate the privlidged user to this creation
    #     """
    #     form.instance.user = self.request.user
    #     return super().form_valid(form)

    # Inherits .as_view(self):


class ClassOfferListView(ListView):
    """ We will want to list the classes that are scheduled to be offered.
    """
    template_name = 'classwork/classoffer_list.html'
    model = ClassOffer
    context_object_name = 'classoffers'

    # def decide_session(self, sess=None):
    #     """ Typically we want to see the current session.
    #         Sometimes we want to see a future sesion.
    #     """
    #     sess_data = []
    #     if sess is None:
    #         today = datetime.now()
    #         sess_data = Session.objects.filter(publiish_date__lte=today, expire_date__gte=today)
    #     else:
    #         # TODO: need to work the logic to grab info sessions
    #         pass
    #     return [ea.name for ea in sess_data]

    # def get_context_data(self, **kwargs):
    #     """ Get the context of the current published classes from Session table
    #     """
    #     today = datetime.now()
    #     context = super().get_context_data(**kwargs)
    #     context['current_session'] = Session.objects.filter(
    #         publiish_date__lte=today,
    #         expire_date__gt=today
    #     ).values('id')[0]['id']  # Only gets the first valid session it finds
    #     return context

    # def get_queryset(self):
    #     """ We can limit the classes list by publish date
    #     """
    #     # today = datetime.now()
    #     # sess_id = Session.objects.filter(
    #     #     publiish_date__lte=today,
    #     #     expire_date__gte=today
    #     # ).values('id')[0]['id']
    #     sess_id = self.context.current_session

    #     return ClassOffer.objects.filter(session=sess_id)


class ClassOfferCreateView(CreateView):
    """ Only appropriate admin level users can create new classes
    """
    template_name = 'classwork/classoffer_create.html'
    model = ClassOffer
    form_class = ClassOfferForm
    success_url = reverse_lazy('classoffer_list')
    # login_url = reverse_lazy('login')

    # def form_valid(self, form):
    #     """ Associate the admin user for this class
    #     """
    #     form.instance.user = self.request.user
    #     return super().form_valid(form)


# class ClassOfferDetailView(DetailView):
#     """ Sometimes we want to show more details for a given class offering
#     """
#     template_name = 'class_info/detail.html'
#     model = ClassOffer
#     context_object_name = 'class'
#     pk_url_kwarg = 'id'

#     def get_context_data(self, **kwargs):
#         """ Modify the context
#         """
#         context = super().get_context_data(**kwargs)
#         # context['added_info'] =
#         return context

#     # def get_queryset(self):
#     #     """ We can limit the classes list by publish date
#     #     """
#     #     return Classes.objects.filter()










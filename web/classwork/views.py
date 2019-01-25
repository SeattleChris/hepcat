from django.views.generic import ListView, CreateView, DetailView
# from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from .models import Subject, Session, ClassOffer, Location
from .forms import SubjectForm, SessionForm, ClassOfferForm
from datetime import datetime
# Create your views here.


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

    # TODO: make decide_session a method that can be imported to various models
    # Unless all places that need this are a model that inhirit from this model.
    def decide_session(self, sess=None, display_date=None):
        """ Typically we want to see the current session.
            Sometimes we want to see a future sesion.
        """
        sess_data = []
        # TODO: Deal with appropriate date input data and test it
        if sess is None:
            target = display_date or datetime.now()
            sess_data = Session.objects.filter(publish_date__lte=target, expire_date__gte=target)
        else:
            if display_date:
                raise SyntaxError("You can't filter by both Session and Date")
            if sess == 'all':
                return Session.objects.all()
            if not isinstance(sess, list):
                sess = [].append(sess)
            try:
                sess_data = Session.objects.filter(name__in=sess)
            except TypeError:
                sess_data = []
        return sess_data  # a list of Session records, even if only 0-1 session

    def get_queryset(self):
        """ We can limit the classes list by class level
        """
        display_session = None
        if 'display_session' in self.kwargs:
            display_session = self.kwargs['display_session']
        sess_id = [ea.id for ea in self.decide_session(sess=display_session)]
        return ClassOffer.objects.filter(session__in=sess_id).order_by('num_level')

    def get_context_data(self, **kwargs):
        """ Get the context of the current published classes from Session table
        """
        context = super().get_context_data(**kwargs)
        # print(context)
        # print('-----------------')
        # print(kwargs)
        display_session = None
        if 'display_session' in kwargs:
            display_session = context['display_session']
        sess_names = [ea.name for ea in self.decide_session(display_session)]
        context['display_session'] = ', '.join(sess_names)
        return context


class Checkin(ListView):
    """ This is a report for which students are in which classes.
    """
    model = ClassOffer
    template_name = 'classwork/checkin.html'
    context_object_name = 'student_list'

    # TODO: make decide_session a method that can be imported to various models
    # Unless all places that need this are a model that inhirit from this model
    def decide_session(self, sess=None, display_date=None):
        """ Typically we want to see the current session.
            Sometimes we want to see a future sesion.
        """
        sess_data = []
        # TODO: Deal with appropriate date input data and test it
        if sess is None:
            target = display_date or datetime.now()
            sess_data = Session.objects.filter(publish_date__lte=target, expire_date__gte=target)
        else:
            if display_date:
                raise SyntaxError("You can't filter by both Session and Date")
            if sess == 'all':
                return Session.objects.all()
            if not isinstance(sess, list):
                sess = [].append(sess)
            try:
                sess_data = Session.objects.filter(name__in=sess)
            except TypeError:
                sess_data = []
        return sess_data  # a list of Session records, even if only 0-1 session

    def get_all_sessions(self):
        sess_list = [a.title for a in Session.objects.all()]
        return sess_list

    def get_queryset(self):
        """ List all the students from all the classes (in order of ClassOffer
            and then alphabetical first name)
        """
        # current_classes = super().get_queryset()
        display_session = None
        if 'display_session' in self.kwargs:
            display_session = self.kwargs['display_session']
        sess_id = [ea.id for ea in self.decide_session(sess=display_session)]
        selected_classes = ClassOffer.objects.filter(session__in=sess_id).order_by('num_level')
        class_list = [ea.students for ea in selected_classes]
        print(class_list)
        print('----------------')
        print(class_list)
        # student_list = [student for student in ea.students for ea in class_list]
        # student_list.order_by('first_name')
        # return student_list
        return class_list

    def get_context_data(self, **kwargs):
        """ Get the context of the current displayed class registration student list
        """
        context = super().get_context_data(**kwargs)
        # print(context)
        # print('-----------------')
        # print(kwargs)
        display_session = None
        if 'display_session' in kwargs:
            display_session = context['display_session']
        sess_names = [ea.name for ea in self.decide_session(display_session)]
        context['display_session'] = ', '.join(sess_names)
        return context

        # class_list = self.get_queryset()
        # # context['student_list'] = ClassOffer.students.filter(
        # #     budget__user__username=self.request.user.username)
        # student_list = []
        # for ea in class_list:
        #     # context[ea.title] = ea.students.order_by('first_name')
        #     student_list.append(ea.students.order_by('user__first_name'))
        # context['student_list'] = student_list
        # # context['students'] = self.students.order_by('first_name')
        # # context['students'] = ['bob', 'joe', 'susan']
        # return context

    # end class Checkin


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


class LocationListView(ListView):
    """ Display all the Locations that we have stored
    """
    template_name = 'classwork/location_list.html'
    model = Location
    context_object_name = 'locations'


class LocationDetailView(DetailView):
    """ Display information for a location
    """
    template_name = 'classwork/location_detail.html'
    model = Location
    context_object_name = 'location'
    pk_url_kwarg = 'id'

    # def get_context_data(self, **kwargs):
    #     """ Modify the context
    #     """
    #     context = super().get_context_data(**kwargs)
    #     context['add_info'] = 'new info'
    #     return context

    # def get_queryset(self):
    #     """ We want to limit what location info we get
    #     """
    #     location_code = get_object_or_404(Location, code=self.kwargs['code'])
    #     return Location.objects.filter(code=location_code)




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










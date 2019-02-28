from django.views.generic import ListView, FormView, CreateView, DetailView, UpdateView

# from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from .models import Location, Subject, Session, ClassOffer, Profile, Registration, Payment
from .forms import SubjectForm, SessionForm, ClassOfferForm, RegisterForm, PaymentForm, ProfileForm, UserForm
import django_tables2 as tables
from django_tables2 import MultiTableMixin
from datetime import datetime
from django.template.response import TemplateResponse  # used for Payments
from payments import get_payment_model, RedirectNeeded  # used for Payments
# Create your views here.


def decide_session(sess=None, display_date=None):
    """ Typically we want to see the current session (returned if no params set)
        Sometimes we want to see a future sesion.
        Used by many views, generally those that need a list of ClassOffers
        that a user can view, sign up for, get a check-in sheet, pay for, etc.
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
    print(sess_data)
    return sess_data  # a list of Session records, even if only 0-1 session


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


class ClassOfferDetailView(DetailView):
    """ Sometimes we want to show more details for a given class offering
    """
    template_name = 'class_info/detail.html'
    model = ClassOffer
    context_object_name = 'class'
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        """ Modify the context
        """
        context = super().get_context_data(**kwargs)
        # context['added_info'] =
        return context

    # def get_queryset(self):
    #     """ We can limit the classes list by publish date
    #     """
    #     return Classes.objects.filter()


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


class ClassOfferListView(ListView):
    """ We will want to list the classes that are scheduled to be offered.
    """
    template_name = 'classwork/classoffer_list.html'
    model = ClassOffer
    context_object_name = 'classoffers'

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

    def get_queryset(self):
        """ We can limit the classes list by class level
        """
        display_session = None
        if 'display_session' in self.kwargs:
            display_session = self.kwargs['display_session']
        # TODO: Change to use the general function instead of self method.
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
        # TODO: Change to use the general function instead of self method.
        sess_names = [ea.name for ea in self.decide_session(display_session)]
        context['display_session'] = ', '.join(sess_names)
        return context


class StudentTable(tables.Table):
    """ Used to display student class check-in info
    """
    from django_tables2 import A

    subj = tables.Column(A('self.taken.all()'))
    pay_type = tables.Column()
    pay_owed = tables.Column()

    class Meta:
        model = Profile


class TableCheckin(MultiTableMixin, ListView):
    table_class = StudentTable
    model = Profile
    template_name = "profile_list.html"

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

    def temp_get_table_data(self):
        """ django_tables2 looks for this to populate the table data.
        """
        # display_session = None
        #     if 'display_session' in self.kwargs:
        #         display_session = self.kwargs['display_session']
        #     session = self.decide_session(sess=display_session)
        #     selected_classes = ClassOffer.objects.filter(session__in=session).order_by('-class_day', 'start_time')
        #     # class_list = [ea.students.all() for ea in selected_classes if hasattr(ea, 'students')]
        #     people = Profile.objects.filter(taken__in=selected_classes)
        #     print('===================')
        #     print(people)
        #     # print(registered)
        #     print('===================')
        #     print(selected_classes)
        #     # print(selected_students)
        #     print('===================')
        #     for ea in selected_classes:
        #         print(ea)
        #         for student in ea.students.all():
        #             print('----------------')
        #             print(student)
        #         print('+++++++++++++++++++')
        #     print('===================')
        #     print(class_list)
        #     return selected_classes
        pass

        # def get_queryset(self):
        #     """ List all the students from all the classes (in order of ClassOffer
        #         and then alphabetical first name)
        #     """
        #     # users = get_user_model()
        #     # current_classes = super().get_queryset()
        #     display_session = None
        #     if 'display_session' in self.kwargs:
        #         display_session = self.kwargs['display_session']
        #     session = self.decide_session(sess=display_session)
        #     selected_classes = ClassOffer.objects.filter(session__in=session).order_by('-class_day', 'start_time')
        #     class_list = [ea.students.all() for ea in selected_classes if hasattr(ea, 'students')]
        #     people = Profile.objects.filter(taken__in=selected_classes)
        #     print('===================')
        #     print(people)
        #     print('===================')
        #     print(selected_classes)
        #     print('===================')
        #     for ea in selected_classes:
        #         print(ea)
        #         for student in ea.students.all():
        #             print('----------------')
        #             print(student)
        #         print('+++++++++++++++++++')
        #     print('===================')
        #     print(class_list)
        #     return selected_classes

        # for MultiTableMixin
        tables = [
            StudentTable(ea.students.all(), exclude=('date_added', 'date_modified',))
            for ea in ClassOffer.objects.all()
        ]
        # tables = [
        #     StudentTable(ea.students.all(), fields=('date_added', 'date_modified',))
        #     for ea in ClassOffer.objects.all()
        # ]

        # def get_context_data(self, **kwargs):
        #     """ Get the context of the current, or selected, class session student list
        #     """
        #     context = super().get_context_data(**kwargs)
        #     display_session = None
        #     if 'display_session' in kwargs:
        #         display_session = context['display_session']
        #     sess_names = [ea.name for ea in self.decide_session(display_session)]
        #     context['display_session'] = ', '.join(sess_names)
        #     return context

    # end class TableCheckin


class Checkin(ListView):
    """ This is a report for which students are in which classes.
    """
    model = ClassOffer
    template_name = 'classwork/checkin.html'
    context_object_name = 'class_list'

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

    # def get_all_sessions(self):
    #     sess_list = [a.title for a in Session.objects.all()]
    #     return sess_list

    def get_queryset(self):
        """ List all the students from all the classes (grouped in days, then
            in start_time order, and then alphabetical first name)
        """
        # users = get_user_model()
        # current_classes = super().get_queryset()
        display_session = None
        if 'display_session' in self.kwargs:
            display_session = self.kwargs['display_session']
        session = self.decide_session(sess=display_session)
        selected_classes = ClassOffer.objects.filter(session__in=session).order_by('-class_day', 'start_time')
        class_list = [ea.students.all() for ea in selected_classes if hasattr(ea, 'students')]
        people = Profile.objects.filter(taken__in=selected_classes)
        # registered = Registration.objects.filter(classoffer__in=selected_classes)
        # selected_students = Profile.objects.filter()
        print('===================')
        print(people)
        # print(registered)
        print('===================')
        print(selected_classes)
        # print(selected_students)
        print('===================')
        for ea in selected_classes:
            print(ea)
            for student in ea.students.all():
                print('----------------')
                print(student)
            print('+++++++++++++++++++')
        print('===================')
        print(class_list)
        return selected_classes

    def get_context_data(self, **kwargs):
        """ Get the context of the current, or selected, class session student list
        """
        context = super().get_context_data(**kwargs)
        display_session = None
        if 'display_session' in kwargs:
            display_session = context['display_session']
        sess_names = [ea.name for ea in self.decide_session(display_session)]
        context['display_session'] = ', '.join(sess_names)
        return context

    # end class Checkin


User = get_user_model()


class RegisterView(CreateView):
    """ Allows a user/student to sign up for a ClassOffer.
        We also want to allow anonymousUser to sign up.
        We want to auto-create a user (and profile) account
        if one does not exist.

        We are using the UpdateView to easily populate the user fields.
    """
    # object_list = ''
    template_name = 'classwork/register.html'
    model = Payment
    form_class = RegisterForm
    # TODO: Can success_url take in payment/registration details?
    # success_url = reverse_lazy('payment_done')
    # finish_url = reverse_lazy('payment_success')
    # failure_url = reverse_lazy('payment_fail')
    test_url = '../payment/done/'
    # TODO: We will need to adjust the payment url stuff later.

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print('========== RegisterView.get_context_data =============')
        # context['user'] = self.request.user
        # sess = context['session'] if context['session'] else None
        # date = context['display_date'] if context['display_date'] else None
        # context['class_choices'] = ClassOffer.objects.filter(session__in=decide_session(sess=sess, display_date=date))
        return context

    # unsure how to accuratly call this one
    # def as_view(**initkwargs):
    #     print('================ as_view =================')
    #     return super().as_view(**initkwargs)

    def dispatch(request, *args, **kwargs):
        print('================ dispatch =================')
        return super(RegisterView, request).dispatch(*args, **kwargs)

    def get(request, *args, **kwargs):
        print('================ get =================')
        return super(RegisterView, request).get(*args, **kwargs)

    def post(request, *args, **kwargs):
        print('================ post =================')
        return super(RegisterView, request).post(*args, **kwargs)

    def put(self, *args, **kwargs):
        print('================ put =================')
        return super().put(*args, **kwargs)

    def get_form(self, form_class=None):
        print('================ get_form =================')
        return super().get_form(form_class)

    def get_form_class(self):
        print('================ get_form_class =================')
        return super().get_form_class()

    def get_form_kwargs(self):
        print('================ get_form_kwargs =================')
        return super(RegisterView, self).get_form_kwargs()

    def get_initial(self):
        print('================ get_initial ====================')
        initial = super().get_initial()
        sess = self.kwargs['session'] if hasattr(self.kwargs, 'session') else None
        date = self.kwargs['display_date'] if hasattr(self.kwargs, 'display_date') else None
        class_choices = ClassOffer.objects.filter(session__in=decide_session(sess=sess, display_date=date))
        initial['class_choices'] = class_choices
        user = self.request.user
        initial['user'] = user
        initial['first_name'] = user.first_name
        initial['last_name'] = user.last_name
        initial['email'] = user.email
        return initial

    def get_prefix(self):
        print('================ get_prefix =================')
        return super().get_prefix()

    # def get_context_data(self, **kwargs):
    #     print('================ get_context_data =================')
    #     return super().get_context_data(**kwargs)

    def render_to_response(self, context, **response_kwargs):
        print('================ render_to_response =================')
        return super(RegisterView, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        print('================ get_template_names =================')
        return super().get_template_names()

    # def form_valid(self, form):
    #     # Inside the following is when the form is called
    #     # to be verified.
    #     # if successful, will return a self.get_success_url
    #     return super(RegisterView, self).form_valid(form)

    def get_success_url(self):
        print('================ get_success_url =================')
        # TODO: We will need to adjust this later.
        url = self.test_url + str(self.object.id)
        print(url)
        return url

    # Unsure after this one.

    def form_invalid(form):
        print('================ form_invalid =================')
        return super().form_invalid(form)

    def get_object(queryset=None):
        print('================ get_object =================')
        return super().get_object(queryset)

    # def head():
    #     print('================ head =================')
    #     return super().head(**initkwargs)

    def http_method_not_allowed(request, *args, **kwargs):
        print('================ http_method_not_allowed =================')
        return super(RegisterView, request).http_method_not_allowed(*args, **kwargs)

    def setup(request, *args, **kwargs):
        print('================ setup =================')
        return super(RegisterView, request).setup(*args, **kwargs)

    def get_context_object_name(self, obj):
        print('================ get_context_object_name =================')
        return super().get_context_object_name(obj)

    def get_queryset(self):
        print('================ get_queryset =================')
        return super().get_queryset()

    def get_slug_field(self):
        print('================ get_slug_field =================')
        return super().get_slug_field()

    def form_valid(self, form):
        # TODO: Extra logic steps done here for our modificaitons.
        print('======== RegisterView.form_valid ========')
        # print('-------- self --------------')
        # print(self)
        # print('------ Self has: ------')
        # for ea in dir(self):
        #     print(ea)
        # print('----------- form ---------------')
        # print(form)

        print('---- Docs say handle unauthorized users in this form_valid ----')
        print('unknown')
        print('------- calling super form_valid ----- ')
        fv = super(RegisterView, self).form_valid(form)
        print('------- printing super RegisterView.form_valid -------')
        print(fv)
        print('==== End RegisterView.form_valid =======')
        return fv

    # end class RegisterView


def payment_done(request):
    return TemplateResponse(request, 'payment/success.html', None)


class PaymentProcessView(UpdateView):
    """ Payment Processing
    """
    template_name = 'payment/payment.html'
    model = Payment
    form_class = PaymentForm
    success_url = reverse_lazy('payment_success')


class PaymentResultView(DetailView):
    """ After a payment attempt, we can have success or failure
    """
    template_name = 'payment/incomplete.html'
    model = Payment
    context_object_name = 'payment'
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print('========== PaymentResultView.get_context_data =============')
        print(kwargs)
        for each in context:
            print(each)
        # payment = context['object']  # for some reason, context['payment'] would also work
        # context['student_name'] = f'{payment.student.first_name} {payment.student.last_name}'
        # if payment.student is not payment.paid_by:
        #     context['paid_by_other'] = True
        #     context['paid_by_name'] = f'{payment.paid_by.first_name} {payment.paid_by.last_name}'
        # context['class_selected'] = payment.description
        # for ea in dir(self):
        #     print(ea)
        # context['user'] = self.request.user
        # sess = context['session'] if context['session'] else None
        # date = context['display_date'] if context['display_date'] else None
        # context['class_choices'] = ClassOffer.objects.filter(session__in=decide_session(sess=sess, display_date=date))
        return context

    def render_to_response(self, context, **response_kwargs):
        print('========= PaymentResultView.render_to_request ========')
        print(context)
        print(response_kwargs)
        return super().render_to_response(context, **response_kwargs)


# def payment_details(request, payment_id):
#     payment = get_object_or_404(get_payment_model(), id=payment_id)
#     try:
#         form = payment.get_form(data=request.POST or None)
#     except RedirectNeeded as redirect_to:
#         return redirect(str(redirect_to))
#     return TemplateResponse(request, 'payment.html',
#                             {'form': form, 'payment': payment})


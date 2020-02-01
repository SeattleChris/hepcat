from django.views.generic import ListView, CreateView, DetailView, UpdateView
# from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from .models import (SiteContent, Resource, Location, ClassOffer, Subject,  # ? Session,
                     Profile, Payment, Registration)
from .forms import RegisterForm, PaymentForm, decide_session  # , ProfileForm, UserForm
from django.shortcuts import get_object_or_404, redirect  # used for Payments
from django.template.response import TemplateResponse  # used for Payments
from payments import get_payment_model, RedirectNeeded  # used for Payments
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
User = get_user_model()

# TODO: Clean out excessive print lines telling us where we are.
# Create your views here.


class AboutUsListView(ListView):
    """ Display details about Business and Staff """
    template_name = 'classwork/aboutus.html'
    model = Profile
    context_object_name = 'profiles'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['business_about'] = SiteContent.objects.get(name='business_about').text
        except ObjectDoesNotExist:
            context['business_about'] = ''
            print('Object Does Not Exist')
        return context

    def get_queryset(self):
        all = super().get_queryset()
        # TODO: only retrieve the staff profiles we want.
        # Profile.objects.filter()
        # TODO: sort them in some desired order.
        return all

    # end AboutUs


class SubjectProgressView(ListView):
    """ More in-depth description of how the Organization expects students to progress through classoffers. """
    template_name = ''
    model = Subject
    context_object_name = 'levels'

    def get_context_data(self, **kwargs):
        """ Modify the context """
        context = super().get_context_data(**kwargs)
        # context['added_info'] =
        return context

    # end SubjectProgressView


class LocationListView(ListView):
    """ Display all the Locations that we have stored """
    # TODO: Should we only list them if a published ClassOffer has them listed?
    # TODO: Should we add a publish flag in the DB for each location?
    template_name = 'classwork/location_list.html'
    model = Location
    context_object_name = 'locations'


class LocationDetailView(DetailView):
    """ Display information for a location """
    template_name = 'classwork/location_detail.html'
    model = Location
    context_object_name = 'location'
    pk_url_kwarg = 'id'


class ClassOfferDetailView(DetailView):
    """ Sometimes we want to show more details for a given class offering """
    template_name = 'classwork/classoffer_detail.html'
    model = ClassOffer
    context_object_name = 'classoffer'
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        """ Modify the context """
        context = super().get_context_data(**kwargs)
        # context['added_info'] =
        return context

    # def get_queryset(self):
    #     """ We can limit the classes list by publish date
    #     """
    #     return Classes.objects.filter()


class ClassOfferListView(ListView):
    """ We will want to list the classes that are scheduled to be offered.
    """
    template_name = 'classwork/classoffer_list.html'
    model = ClassOffer
    context_object_name = 'classoffers'
    # TODO: Make more DRY between get_queryset & get_context_data. Determine
    # which is used first and if the info is accessible to the other.

    def get_queryset(self):
        """ We can limit the classes list by class level """
        display_session = self.kwargs.get('display_session', None)
        # display_session = None
        # if 'display_session' in self.kwargs:
        #     display_session = self.kwargs['display_session']  # TODO: change to ternary assignment
        sess_id = [ea.id for ea in decide_session(sess=display_session)]
        return ClassOffer.objects.filter(session__in=sess_id).order_by('num_level')

    def get_context_data(self, **kwargs):
        """ Get the context of the current published classes from Session table """
        context = super().get_context_data(**kwargs)
        display_session = context.get('display_session', None)
        # display_session = None
        # if 'display_session' in kwargs:
        #     display_session = context['display_session']  # TODO: change to ternary assignment
        sess_names = [ea.name for ea in decide_session(display_session)]
        context['display_session'] = ', '.join(sess_names)
        return context


class Checkin(ListView):
    """ This is a report for which students are in which classes. """
    model = ClassOffer
    template_name = 'classwork/checkin.html'
    context_object_name = 'class_list'

    def get_queryset(self):
        """ List all the students from all the classes (grouped in days, then
            in start_time order, and then alphabetical first name)
        """
        # current_classes = super().get_queryset()
        display_session = None
        if 'display_session' in self.kwargs:
            display_session = self.kwargs['display_session']  # TODO: change to ternary assignment
        session = decide_session(sess=display_session)
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
        """ Get the context of the current, or selected, class session student list """
        context = super().get_context_data(**kwargs)
        display_session = None
        if 'display_session' in kwargs:
            display_session = context['display_session']  # TODO: change to ternary assignment
        sess_names = [ea.name for ea in decide_session(display_session)]
        context['display_session'] = ', '.join(sess_names)
        return context

    # end class Checkin


class ResourceDetailView(DetailView):
    """ Each Resource can be viewed if the user has permission """
    model = Resource
    context_object_name = 'resource'
    pk_url_kwarg = 'id'
    template_name = 'classwork/resource.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["type"] = self.object.content_type
        return context

    # end ResourceDetailView


class ProfileView(DetailView):
    """Each user has a page where they can see resources that have been made
        available to them.
    """
    template_name = 'classwork/user.html'
    model = Profile
    context_object_name = 'profile'
    pk_url_kwarg = 'id'
    # TODO: Work on the actual layout and presentation of the avail Resources
    # TODO: Filter out the resources that are not meant for ProfileView

    def get_object(self):
        print('=== ProfileView get_object ====')
        return Profile.objects.get(user=self.request.user)

    def get_context_data(self, **kwargs):
        """ Modify the context """
        context = super().get_context_data(**kwargs)
        print('===== ProfileView get_context_data ======')
        registers = list(Registration.objects.filter(student=self.object).values('classoffer'))
        ids = list(set([list(ea.values())[0] for ea in registers]))
        taken = ClassOffer.objects.filter(id__in=ids)
        print(ids)
        res = []
        for ea in ids:
            cur = ClassOffer.objects.get(id=ea)
            cur_res = [res for res in Resource.objects.filter(
                Q(classoffer=cur) |
                Q(subject=cur.subject)
                ) if res.publish(cur)]
            res.extend(cur_res) if len(cur_res) else None
        print('----- res ------')
        print(res)
        context['had'] = taken
        ct = {ea[0]: [] for ea in Resource.CONTENT_CHOICES}
        [ct[ea.content_type].append(ea) for ea in res]
        # ct is now is a dictionary of all possible content types, with values
        # of the current user resources that are past their avail date.
        context['resources'] = {key: vals for (key, vals) in ct.items() if len(vals) > 0}
        # context['resources'] only has the ct keys if the values have data.
        print(context['resources'])
        return context

    # end class ProfileView


class RegisterView(CreateView):
    """ Allows a user/student to sign up for a ClassOffer.
        We also want to allow anonymousUser to sign up, creating a new user (and profile) as needed.
        Payment model is instantiated, student is added to the ClassOffer list.
    """
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

    # unsure how to accurately call this one
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
        return super().post(request, *args, **kwargs)

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
        print(user)
        if not user.is_anonymous:
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
        print('================ RegisterView.get_success_url =================')
        # TODO: We will need to adjust this later.
        # url = self.test_url + str(self.object.id)
        url = '../payment/' + str(self.object.id)
        print(url)
        return url

    # Unsure after this one.

    def form_invalid(self, form):
        print('================ form_invalid =================')
        print(f'Self: {self}')
        for ea in dir(self):
            print(ea)
        print(f'Form: {form}')
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
        # TODO: Extra logic steps done here for our modifications.
        print('======== RegisterView.form_valid ========')
        # print('-------- self --------------')
        # print(self)
        # print('------ Self has: ------')
        # for ea in dir(self):
        #     print(ea)
        # print('----------- form ---------------')
        # print(form)

        print('---- Docs say handle unauthorized users in this form_valid ----')
        print('------- calling super form_valid ----- ')
        fv = super(RegisterView, self).form_valid(form)
        print('------- printing super RegisterView.form_valid -------')
        print(fv)
        print('==== End RegisterView.form_valid =======')
        return fv

    # end class RegisterView


class PaymentProcessView(UpdateView):
    """ Payment Processing.
        The RegisterView is the create for a payment which sends an authorization request.
        Here, we receive the authorization request and handle the next steps.
        - Error: Something did not work in the Authorization request
            - Payment left as incomplete. Request new payment.
        - Incomplete: User was sent to make a payment, but they did not finish.
            - Payment left as incomplete. Request new payment.
        - Authorize Fail: User tried to pay, but could not authorize the payment.
            - Payment left as incomplete. Request new payment.
        - Authorized: Using Authorize & Capture, so we now need to Capture.
            - ? Confirm the authorized amount matches the expected total amount?
            - Update the Payment model with Authorize details.
            - Start process that issues a payment.capture()
        - Captured: We already requested, and were successful, in getting the Capture.
            - Confirm the captured amount is the expected total and/or mark as partial payment.
            - Update the Payment model with Capture details.
            - Make sure the checkin, profile, etc all know this payment is complete (or partial)
        - Capture Fail: We tried, but an authorized capture did not work.
            - Retry later?
            - Make sure the payment is incomplete - Marked as still authorized?
        - Refund ??
        See Payment statuses: https://django-payments.readthedocs.io/en/latest/usage.html
    """
    # template_name = 'classwork/register.html'  # matches create form
    template_name = 'payment/success.html'  # matches PaymentForm form_class
    model = Payment
    context_object_name = 'payment'
    pk_url_kwarg = 'id'
    form_class = PaymentForm   # only payment fields, not same as the create view
    # form_class = RegisterForm  # matches the create view
    # success_url = reverse_lazy('payment_success')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print('========== PaymentResultView.get_context_data =============')
        payment = context['object']  # context['payment'] would also work
        if payment.status == 'preauth':
            print('------------ Payment Capture -------------------')
            payment.capture()
        # TODO: put in logic for handling refunds, release, etc.
        context['payment_done'] = True if payment.status == 'confirmed' else False
        context['student_name'] = f'{payment.student.user.first_name} {payment.student.user.last_name}'
        if payment.student != payment.paid_by:
            # TODO: Check the logic of this if statement
            context['paid_by_other'] = True
            context['paid_by_name'] = f'{payment.paid_by.user.first_name} {payment.paid_by.user.last_name}'
        context['class_selected'] = payment.description
        return context

    def render_to_response(self, context, **response_kwargs):
        print('========= PaymentResultView.render_to_response ========')
        print(context)
        print('------------ Context vs Response kwargs -------------------')
        print(response_kwargs)
        return super().render_to_response(context, **response_kwargs)

    # end class PaymentProcessView


def payment_details(request, id):
    """ This is based on the django-payments docs. """
    print('========== views function - payment_details ==============')
    payment = get_object_or_404(get_payment_model(), id=id)
    try:
        form = payment.get_form(data=request.POST or None)
    except RedirectNeeded as redirect_to:
        print('---- payment_details redirected -------')
        return redirect(str(redirect_to))
    # form.initial = {'billing_email': payment.billing_email}
    print('------ payment_details TemplateResponse ---------')
    return TemplateResponse(request, 'payment/payment.html',
                            {'form': form, 'payment': payment})

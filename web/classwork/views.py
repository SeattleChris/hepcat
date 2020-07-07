from django.views.generic import ListView, CreateView, DetailView, UpdateView
# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404, redirect  # used for Payments
from django.template.response import TemplateResponse  # used for Payments
from payments import get_payment_model, RedirectNeeded  # used for Payments
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from .forms import RegisterForm, PaymentForm  # , ProfileForm, UserForm
from .models import (SiteContent, Resource, Location, ClassOffer, Subject,  # ? Session,
                     Profile, Payment, Registration, Session)
from datetime import datetime
User = get_user_model()

# TODO: Clean out excessive print lines telling us where we are.


def decide_session(sess=None, display_date=None):
    """ Typically we want to see the current session (returned if no params set)
        Sometimes we want to see a future session.
        Used by many views, generally those that need a list of ClassOffers
        that a user can view, sign up for, get a check-in sheet, pay for, etc.
        Returns a list always, even if an empty list.
    """
    query = Session.objects
    if sess is None:
        target = display_date or datetime.now()
        query = query.filter(publish_date__lte=target, expire_date__gte=target)
    elif display_date:
        raise SyntaxError(_("You can't filter by both Session and Display Date"))
    elif sess != 'all':
        if not isinstance(sess, list):
            sess = [sess]
        query = query.filter(name__in=sess)
    sess_data = query.all()
    if not sess_data and not sess:
        result = Session.objects.filter(publish_date__lte=target).order_by('-key_day_date').first()
        sess_data = [result] if result else []
    return sess_data  # a list of Session records, even if only 0-1 session


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
        staff = all.filter(user__is_staff=True)
        # TODO: sort them in some desired order.
        return staff

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
    display_session = None  # 'all' or <start_month>_<year> as stored in DB Session.name
    display_date = None     # <year>-<month>-<day>

    def get_queryset(self):
        """ We can limit the classes list by session, what is published on a given date, or currently published. """
        print("============ ClassOfferListView.get_queryset ================")
        display_session = self.kwargs.get('display_session', None)
        display_date = self.kwargs.get('display_date', None)
        sessions = decide_session(sess=display_session, display_date=display_date)
        self.kwargs['sessions'] = sessions
        return ClassOffer.objects.filter(session__in=sessions).order_by('num_level')

    def get_context_data(self, **kwargs):
        """ Get context of class list we are showing, typically currently published or modified by URL parameters """
        print("============ ClassOfferListView.get_context_data ================")
        context = super().get_context_data(**kwargs)
        sessions = self.kwargs.pop('sessions', None)
        context['sessions'] = ', '.join([ea.name for ea in sessions])
        context['display_session'] = self.kwargs.pop('display_session', None)
        context['display_date'] = self.kwargs.pop('display_date', None)
        return context


class Checkin(ListView):
    """ This is a report for which students are in which classes. """
    model = Registration
    template_name = 'classwork/checkin.html'
    context_object_name = 'class_list'
    display_session = None  # 'all' or <start_month>_<year> as stored in DB Session.name

    def get_queryset(self):
        """ List all the students from all the classes (grouped in days, then
            in start_time order, and then alphabetical first name)
        """
        print("============ Checkin.get_queryset ================")
        display_session = self.kwargs.get('display_session', None)
        display_date = self.kwargs.get('display_date', None)
        sessions = decide_session(sess=display_session, display_date=display_date)
        self.kwargs['sessions'] = sessions
        selected_classes = ClassOffer.objects.filter(session__in=sessions).order_by('-class_day', 'start_time')
        return selected_classes

    def get_context_data(self, **kwargs):
        """ Get the context of the current, or selected, class session student list """
        print("============ Checkin.get_context_data ================")
        context = super().get_context_data(**kwargs)
        sessions = self.kwargs.pop('sessions', None)
        context['sessions'] = ', '.join([ea.name for ea in sessions])
        context['display_session'] = self.kwargs.pop('display_session', None)
        context['display_date'] = self.kwargs.pop('display_date', None)
        earliest, latest = None, None
        if context['display_session'] != 'all':
            earliest = sessions.order_by('key_day_date').first()
            latest = sessions.order_by('-key_day_date').first()
        context['prev_session'] = earliest.prev_session if earliest else None
        context['next_session'] = latest.next_session if latest else None
        return context


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
    display_session = None  # 'all' or <start_month>_<year> as stored in DB Session.name
    display_date = None     # <year>-<month>-<day>
    # TODO: Can success_url take in payment/registration details?
    # success_url = reverse_lazy('payment_done')
    # finish_url = reverse_lazy('payment_success')
    # failure_url = reverse_lazy('payment_fail')
    test_url = '../payment/done/'
    # TODO: We will need to adjust the payment url stuff later.

    # unsure how to accurately call this one
    # def as_view(**initkwargs):
    #     print('================ as_view =================')
    #     return super().as_view(**initkwargs)

    def setup(self, *args, **kwargs):
        print('================ RegisterView.setup =================')
        return super(RegisterView, self).setup(*args, **kwargs)

    def dispatch(self, *args, **kwargs):
        print('================ RegisterView.dispatch =================')
        return super(RegisterView, self).dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        print('================ RegisterView.get =================')
        return super(RegisterView, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        print('================ RegisterView.post =================')
        return super().post(self, *args, **kwargs)

    def put(self, *args, **kwargs):
        print('================ RegisterView.put =================')
        return super().put(*args, **kwargs)

    def get_context_data(self, **kwargs):
        print('========== RegisterView.get_context_data =============')
        context = super().get_context_data(**kwargs)
        print(context)
        return context

    def get_form(self, form_class=None):
        print('================ RegisterView.get_form =================')
        return super().get_form(form_class)

    def get_form_class(self):
        print('================ RegisterView.get_form_class =================')
        return super().get_form_class()

    def get_form_kwargs(self):
        print('================ RegisterView.get_form_kwargs =================')
        kwargs = super(RegisterView, self).get_form_kwargs()
        sess = self.kwargs.get('display_session', None)
        date = self.kwargs.get('display_date', None)
        class_choices = ClassOffer.objects.filter(session__in=decide_session(sess=sess, display_date=date))
        kwargs['class_choices'] = class_choices
        return kwargs

    def get_initial(self):
        print('================ RegisterView.get_initial ====================')
        initial = super().get_initial()
        user = self.request.user
        home_state = User._meta.get_field('billing_country_area').get_default()
        initial['user'] = user
        print(user)
        print('------- Update initial Values --------------')
        initial['first_name'] = getattr(user, 'first_name', '')
        initial['last_name'] = getattr(user, 'last_name', '')
        initial['email'] = getattr(user, 'email', '')
        initial['billing_address_1'] = getattr(user, 'billing_address_1', '')
        initial['billing_address_2'] = getattr(user, 'billing_address_2', '')
        initial['billing_country_area'] = getattr(user, 'billing_country_area', home_state)
        initial['billing_postcode'] = getattr(user, 'billing_postcode', '')
        print(initial)
        return initial

    def get_prefix(self):
        print('================ RegisterView.get_prefix =================')
        return super().get_prefix()

    def render_to_response(self, context, **response_kwargs):
        print('================ RegisterView.render_to_response =================')
        return super(RegisterView, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        print('================ RegisterView.get_template_names =================')
        return super().get_template_names()

    def form_valid(self, form):
        print('======== RegisterView.form_valid ========')
        print('---- Docs say handle unauthorized users in this form_valid ----')
        fv = super(RegisterView, self).form_valid(form)
        print(fv)
        return fv

    def get_success_url(self):
        print('================ RegisterView.get_success_url =================')
        # TODO: We will need to adjust this later.
        # url = self.test_url + str(self.object.id)
        url = '../payment/' + str(self.object.id)
        print(url)
        return url

    # Unsure after this one.

    def form_invalid(self, form):
        print('================ RegisterView.form_invalid =================')
        print(f'Self: {self}')
        for ea in dir(self):
            print(ea)
        print(f'Form: {form}')
        return super().form_invalid(form)

    def get_object(self, queryset=None):
        print('================ RegisterView.get_object =================')
        return super().get_object(queryset)

    # def head():
    #     print('================ head =================')
    #     return super().head(**initkwargs)

    def http_method_not_allowed(self, *args, **kwargs):
        print('================ RegisterView.http_method_not_allowed =================')
        return super(RegisterView, self).http_method_not_allowed(*args, **kwargs)

    def get_context_object_name(self, obj):
        print('================ RegisterView.get_context_object_name =================')
        return super().get_context_object_name(obj)

    def get_queryset(self):
        print('================ RegisterView.get_queryset =================')
        return super().get_queryset()

    def get_slug_field(self):
        print('================ RegisterView.get_slug_field =================')
        return super().get_slug_field()

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


def payment_details(self, id):
    """ The route for this function is called by django-payments after a registration is submitted. """
    print('========== views function - payment_details ==============')
    payment = get_object_or_404(get_payment_model(), id=id)
    try:
        form = payment.get_form(data=self.POST or None)
    except RedirectNeeded as redirect_to:
        print('---- payment_details redirected -------')
        return redirect(str(redirect_to))
    print('------ payment_details TemplateResponse ---------')
    return TemplateResponse(self, 'payment/payment.html',
                            {'form': form, 'payment': payment})

from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.template.response import TemplateResponse  # used for Payments
from django.shortcuts import get_object_or_404, redirect  # used for Payments
from payments import get_payment_model, RedirectNeeded  # used for Payments
# from django.core.cache import caches  # This is not correct.
from django.core.cache import cache
# from django.views.decorators.cache import cache_page
# from django.views.decorators.vary import vary_on_cookie, vary_on_headers
# from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist  # , PermissionDenied
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin  # , LoginRequiredMixin
# from django.contrib.admin.views.decorators import staff_member_required  # TODO: Add decorator to needed views.
from .forms import RegisterForm, PaymentForm
from .models import (SiteContent, Resource, Location, ClassOffer, Subject,  # ? Session, Student
                     Staff, Payment, Registration, Session)
from datetime import datetime as dt
# from pprint import pprint
User = get_user_model()


def decide_session(sess=None, display_date=None, return_key=False):
    """Typically we want to see the current session (default values), sometimes we want to see different session(s).
        Used chiefly by ClassOfferListView, CheckIn, and RegisterView, but could be used elsewhere for session context.
        Return if 'display_date' is set:
        Query of zero or more Sessions that were live on that given date.
        Return if 'sess' is a provided string:
        Query of Session(s) matching the one name given, or any names given in a comma-seperated list.
        Return if 'sess' and 'display_date' are None:
        Query of (typically only one) currently live Sessions if any, or a list with only the most recently expired one.
    """
    if display_date and sess:
        raise SyntaxError(_("You can't filter by both Session and Display Date"))
    key_cache = 'current_session' if not sess and not display_date else sess
    data_cache = None if not key_cache else cache.get(key_cache)
    if data_cache:
        return (data_cache, key_cache) if return_key else data_cache
    # Otherwise not in cache. Find it, add to cache (except if determining by display_date), and return the session.
    query = Session.objects
    target = display_date or dt.now().date()
    if sess is None:
        query = query.filter(publish_date__lte=target, expire_date__gte=target)
    elif sess != 'all':  # the query will be for all if sess == 'all'.
        if not isinstance(sess, str):
            raise TypeError(_("Parameter 'sess' expected a string with possible comma-seperated values. "))
        sess = sess.split(',')
        query = query.filter(name__in=sess)
    # sess_data = query if query.exists() else None  # Check exists() better only if query is modified before evaluated.
    sess_data = query.all()
    if not sess_data and not sess:  # No upcoming published sessions, return most recent previous session.
        key_cache = None  # Turns off storing this in the cache. Allows a new 'current_session' if a session is added.
        try:
            result = Session.objects.filter(publish_date__lte=target).latest('key_day_date')  # TODO: Ensure full sess?
        except Session.DoesNotExist:
            result = None
        sess_data = [result] if result else Session.objects.none()
    if key_cache and sess_data:  # Add to cache with expiration depending on session.
        end_date = sess_data[0].expire_date  # Note: target is always today if we are adding to the cache.
        if key_cache == 'current_session':
            expire_in = end_date - target  # end when the session expires.
            expire_in = int(expire_in.total_seconds())
        elif end_date and end_date < target:
            expire_in = 60 * 60 * 24 * 7  # one week
        else:  # end_date >= today or end_date is None.
            expire_in = 60 * 15  # 15 minutes
        cache.set(key_cache, sess_data, expire_in)
    if return_key:
        return sess_data, key_cache
    return sess_data  # a list of Session records, even if only 0-1 session


class ViewOnlyForTeacherOrAdminMixin(UserPassesTestMixin):
    """Raises PermissionDenied for a User not in a required_group.
        raise_exception: As False (default) will login redirect AnonymousUser. As True, will raise PermissionDenied.
        permission_denied_message: May display in the 403 error page, depending on the template & view. Can be updated.
    """
    required_group = ('teacher', 'admin', )
    login_url = reverse_lazy('login')
    raise_exception = False
    permission_denied_message = 'You scoundrel! You do not have access to that page. That page may not even exist!'

    def test_func(self):
        """Expected to return a boolean representing if the user is allowed access to this view. """
        if not self.request.user.is_authenticated:
            return False
        # user_groups = set([group for group in self.request.user.groups.values_list('name', flat=True)])
        user_groups = set(group for group in self.request.user.groups.values_list('name', flat=True))
        if len(user_groups.intersection(self.required_group)) < 1:
            self.permission_denied_message = f"{self.request.user}, " + self.permission_denied_message
            return False
        return True


class AboutUsListView(ListView):
    """Display details about Business and Staff """
    template_name = 'classwork/aboutus.html'
    model = Staff
    context_object_name = 'profiles'
    queryset = Staff.objects.filter(user__is_active=True, listing__gt=-1)  # user__is_staff=True,
    ordering = ('listing', )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            about = SiteContent.objects.get(name='business_about')
        except ObjectDoesNotExist:
            about = None
        context['business_about'] = getattr(about, 'text', None) if about else ''
        return context


class SubjectProgressView(ListView):
    """Not yet implemented. More in-depth description of how students are expected to progress through classoffers. """
    template_name = ''
    model = Subject
    context_object_name = 'levels'


class LocationListView(ListView):
    """Display all the Locations that we have stored """
    # TODO: Should we only list them if a published ClassOffer has them listed?
    template_name = 'classwork/location_list.html'
    model = Location
    context_object_name = 'locations'


class LocationDetailView(DetailView):
    """Display information for a location """
    template_name = 'classwork/location_detail.html'
    model = Location
    context_object_name = 'location'
    pk_url_kwarg = 'id'


class ClassOfferDetailView(DetailView):
    """Sometimes we want to show more details for a given class offering """
    template_name = 'classwork/classoffer_detail.html'
    model = ClassOffer
    context_object_name = 'classoffer'
    pk_url_kwarg = 'id'


class ClassOfferListView(ListView):
    """We will want to list the classes that are scheduled to be offered. """
    template_name = 'classwork/classoffer_list.html'
    template_admin = 'classwork/classoffer_list_admin.html'
    model = ClassOffer
    context_object_name = 'classoffers'
    display_session = None  # 'all' or <start_month>_<year> as stored in DB Session.name
    display_date = None     # <year>-<month>-<day>
    query_order_by = ('session__key_day_date', '_num_level', )  # TODO: ? Refactor to Meta: ordering(...) ?

    def get_queryset(self):
        """We can limit the classes list by session, what is published on a given date, or currently published. """
        print("=============== ClassOfferListView.get_queryset ===============")
        display_session = self.kwargs.get('display_session', None)
        display_date = self.kwargs.get('display_date', None)
        if display_date and display_session:
            raise SyntaxError(_("You can't filter by both Session and Display Date"))
        key_cache = 'current_session' if not display_session and not display_date else display_session
        sessions, data_cache, sess_key = None, None, None
        if key_cache:
            sessions, data_cache = cache.get(f"{key_cache}_classes", (None, None))
        if not sessions:
            sessions, sess_key = decide_session(sess=display_session, display_date=display_date, return_key=True)
        self.kwargs['sessions'] = sessions
        if data_cache:
            return data_cache
        q = ClassOffer.objects.filter(session__in=sessions)
        q = q.order_by(*self.query_order_by) if getattr(self, 'query_order_by', None) else q
        q = q.select_related('subject', 'session', 'location').prefetch_related('teachers')
        if sess_key and key_cache and sessions:  # False if query by date or no current session,
            end_date = sessions[0].expire_date
            today = dt.now().date()
            if key_cache == 'current_session':
                expire_in = end_date - today  # end when the session expires.
                expire_in = int(expire_in.total_seconds())
            elif end_date and end_date < today:
                expire_in = 60 * 60 * 24 * 7  # one week
            else:  # end_date >= today or end_date is None.
                expire_in = 60 * 15  # 15 minutes
            q = q.all()
            cache.set(f"{key_cache}_classes", (sessions, q), expire_in)
        return q

    def get_context_data(self, **kwargs):
        """Get context of class list we are showing, typically currently published or modified by URL parameters """
        print("=============== ClassOfferListView.get_context_data ===============")
        # pprint(cache)
        # print("----------------------------------------------------------------")
        # test_val = cache.get('test')
        # if test_val:
        #     print(f"Found the test val: {test_val} ")
        # else:
        #     cache.set('test', 'add-this-value')
        #     print("Added a value")
        context = super().get_context_data(**kwargs)
        sessions = self.kwargs.pop('sessions', '')
        sessions = ', '.join(ea.name for ea in sessions)
        context['sessions'] = sessions
        if self.request.user.is_staff:
            admin_log = [sessions, self.kwargs.pop('display_session', 'None'), self.kwargs.pop('display_date', 'None')]
            context['admin_log'] = ' | '.join(admin_log)
        return context

    def get_template_names(self):
        if self.template_admin and self.request.user.is_staff:
            return [self.template_admin]
        return super().get_template_names()


class Checkin(ViewOnlyForTeacherOrAdminMixin, ListView):
    """This is a report for which students are in which classes. """
    group_required = ('teacher', 'admin', )
    model = Registration  # context_object_name = 'object_list'
    template_name = 'classwork/checkin.html'
    display_session = None  # 'all' or <start_month>_<year> as stored in DB Session.name
    query_order_by = ('classoffer__session__key_day_date', '-classoffer__class_day', 'classoffer__start_time', )
    # TODO: ? Refactor to Meta: ordering(...) ?

    def get_queryset(self):
        """List all the students from all the classes sorted according to the class property query_order_by.
            Student list should be grouped in days, then in start_time order, and then alphabetical first name.
        """
        display_session = self.kwargs.get('display_session', None)
        display_date = self.kwargs.get('display_date', None)
        sessions = decide_session(sess=display_session, display_date=display_date)
        self.kwargs['sessions'] = sessions
        q = self.model.objects.filter(classoffer__session__in=sessions)
        q = q.order_by(*self.query_order_by)
        q = q.select_related('classoffer__subject', 'student', 'student__user', 'payment')
        return q

    def get_context_data(self, **kwargs):
        """Determine Session filter parameters. Reference to previous and next Session if feasible. """
        context = super().get_context_data(**kwargs)
        sessions = self.kwargs.pop('sessions', [])
        context['sessions'] = ', '.join(ea.name for ea in sessions)
        context['display_session'] = self.kwargs.pop('display_session', None)  # Currently not used in webpage
        context['display_date'] = self.kwargs.pop('display_date', None)  # Currently not used
        earliest, latest = None, None
        if context['display_session'] != 'all':
            if isinstance(sessions, list) and len(sessions):  # TODO: Find Django function to order model instances.
                earliest = sessions[0]
                latest = sessions[-1]
            else:
                earliest = sessions.earliest('key_day_date')
                latest = sessions.latest('key_day_date')
        context['prev_session'] = getattr(earliest, 'prev_session', None)  # earliest.prev_session if earliest else None
        context['next_session'] = getattr(latest, 'next_session', None)    # latest.next_session if latest else None
        return context


class ResourceDetailView(DetailView):
    """Each Resource can be viewed if the user has permission """
    model = Resource
    context_object_name = 'resource'
    pk_url_kwarg = 'id'
    template_name = 'classwork/resource.html'


class ProfileView(DetailView):
    """Each user has a page where they can see resources that have been made available to them. """
    template_name = 'classwork/user.html'
    profile_type = ''
    context_object_name = 'profile'
    pk_url_kwarg = 'id'
    # TODO: Work on the actual layout and presentation of the avail Resources
    # TODO: Filter out the resources that are not meant for ProfileView

    def get_object(self):
        user = self.request.user
        if 'id' in self.kwargs:
            if user.is_admin:
                try:
                    user = User.objects.get(id=self.kwargs['id'])
                except User.DoesNotExist as e:
                    raise e
        if self.profile_type:
            profile = getattr(user, self.profile_type, None)
            if not profile:
                raise ObjectDoesNotExist(_("User {} does not have a {} profile.".format(user, self.profile_type)))
        else:
            profile = getattr(user, 'profile', user.staff if user.is_staff else getattr(user, 'student', None))
            self.profile_type = '' if profile is None else str(profile._meta.model_name)
        return profile

    def make_resource_dict(self, co_connected):
        # TODO: Revisit the following for better dictionary creation.
        ct = {ea[0]: [] for ea in Resource.CONTENT_CHOICES}
        [ct[ea.get('content_type', None)].append(ea) for ea in co_connected.resources().all()]
        # return is a dict that only has the ct keys if the values have data.
        return {key: vals for (key, vals) in ct.items() if len(vals) > 0}

    def get_context_data(self, **kwargs):
        """Modify the context """
        context = super().get_context_data(**kwargs)
        co_connected = getattr(context['object'], 'taken' if self.profile_type == 'student' else 'taught', object)
        context['classoffers'] = co_connected.all()
        context['resources'] = self.make_resource_dict(co_connected)
        context['profile_type'] = self.profile_type
        return context


class RegisterView(CreateView):
    """Allows a user/student to sign up for a ClassOffer.
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
    initial = {
        'billing_country_area': settings.DEFAULT_COUNTRY_AREA_STATE,
    }

    # unsure how to accurately call this one
    # def as_view(**initkwargs):
    #     print('================ as_view =================')
    #     return super().as_view(**initkwargs)

    # def setup(self, *args, **kwargs):
    #     print('================ RegisterView.setup =================')
    #     return super(RegisterView, self).setup(*args, **kwargs)

    # def dispatch(self, *args, **kwargs):
    #     print('================ RegisterView.dispatch =================')
    #     return super(RegisterView, self).dispatch(*args, **kwargs)

    # def get(self, *args, **kwargs):
    #     print('================ RegisterView.get =================')
    #     return super(RegisterView, self).get(*args, **kwargs)

    # def post(self, *args, **kwargs):
    #     print('================ RegisterView.post =================')
    #     return super().post(self, *args, **kwargs)

    # def put(self, *args, **kwargs):
    #     print('================ RegisterView.put =================')
    #     return super().put(*args, **kwargs)

    # def get_context_data(self, **kwargs):
    #     print('========== RegisterView.get_context_data =============')
    #     context = super().get_context_data(**kwargs)
    #     print(context)
    #     return context

    # def get_form(self, form_class=None):
    #     # print('================ RegisterView.get_form =================')
    #     form = super().get_form(form_class)
    #     # print('---------------------- form -----------------------------')
    #     # print(form)
    #     # print('---------------------- form done -----------------------------')
    #     return form

    # def get_form_class(self):
    #     print('================ RegisterView.get_form_class =================')
    #     return super().get_form_class()

    def get_form_kwargs(self):
        # print('================ RegisterView.get_form_kwargs =================')
        kwargs = super(RegisterView, self).get_form_kwargs()
        sess = self.kwargs.get('display_session', None)
        display_date = self.kwargs.get('display_date', None)
        class_choices = ClassOffer.objects.filter(session__in=decide_session(sess=sess, display_date=display_date))
        kwargs['class_choices'] = class_choices
        return kwargs

    def get_initial(self):
        # print('================ RegisterView.get_initial ====================')
        initial = super().get_initial()
        default_area = initial.get('billing_country_area', '')
        user = self.request.user
        initial['user'] = user
        if not user.is_anonymous:
            initial['first_name'] = getattr(user, 'first_name', '')
            initial['last_name'] = getattr(user, 'last_name', '')
            initial['email'] = getattr(user, 'email', '')
            initial['billing_address_1'] = getattr(user, 'billing_address_1', '')
            initial['billing_address_2'] = getattr(user, 'billing_address_2', '')
            initial['billing_country_area'] = getattr(user, 'billing_country_area', default_area)
            initial['billing_postcode'] = getattr(user, 'billing_postcode', '')
        return initial

    # def get_prefix(self):
    #     print('================ RegisterView.get_prefix =================')
    #     return super().get_prefix()

    # def render_to_response(self, context, **response_kwargs):
    #     print('================ RegisterView.render_to_response =================')
    #     return super(RegisterView, self).render_to_response(context, **response_kwargs)

    # def get_template_names(self):
    #     print('================ RegisterView.get_template_names =================')
    #     return super().get_template_names()

    # def form_valid(self, form):
    #     print('======== RegisterView.form_valid ========')
    #     print('---- Docs say handle unauthorized users in this form_valid ----')
    #     fv = super(RegisterView, self).form_valid(form)
    #     print(fv)
    #     return fv

    def get_success_url(self):
        print('================ RegisterView.get_success_url =================')
        # TODO: We will need to adjust this later.
        # url = self.test_url + str(self.object.id)
        url = '../payment/' + str(self.object.id)
        print(url)
        return url

    # Unsure after this one.

    # def form_invalid(self, form):
    #     print('================ RegisterView.form_invalid =================')
    #     print(f'Self: {self}')
    #     for ea in dir(self):
    #         print(ea)
    #     print(f'Form: {form}')
    #     return super().form_invalid(form)

    # def get_object(self, queryset=None):
    #     print('================ RegisterView.get_object =================')
    #     return super().get_object(queryset)

    # # def head():
    # #     print('================ head =================')
    # #     return super().head(**initkwargs)

    # def http_method_not_allowed(self, *args, **kwargs):
    #     print('================ RegisterView.http_method_not_allowed =================')
    #     return super(RegisterView, self).http_method_not_allowed(*args, **kwargs)

    # def get_context_object_name(self, obj):
    #     print('================ RegisterView.get_context_object_name =================')
    #     return super().get_context_object_name(obj)

    # def get_queryset(self):
    #     print('================ RegisterView.get_queryset =================')
    #     return super().get_queryset()

    # def get_slug_field(self):
    #     print('================ RegisterView.get_slug_field =================')
    #     return super().get_slug_field()

    # end class RegisterView


class PaymentProcessView(UpdateView):
    """Payment Processing.
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
        # print('========== PaymentResultView.get_context_data =============')
        payment = context['object']  # context['payment'] would also work
        if payment.status == 'preauth':
            # print('------------ Payment Capture -------------------')
            payment.capture()
        # TODO: put in logic for handling refunds, release, etc.
        context['payment_done'] = True if payment.status == 'confirmed' else False
        context['student_name'] = f'{payment.student.user.first_name} {payment.student.user.last_name}'
        if payment.student != payment.paid_by:
            context['paid_by_other'] = True
            context['paid_by_name'] = f'{payment.paid_by.user.first_name} {payment.paid_by.user.last_name}'
        context['class_selected'] = payment.description
        return context

    # def render_to_response(self, context, **response_kwargs):
    #     print('========= PaymentResultView.render_to_response ========')
    #     print(context)
    #     print('------------ Context vs Response kwargs -------------------')
    #     print(response_kwargs)
    #     return super().render_to_response(context, **response_kwargs)

    # end class PaymentProcessView


def payment_details(self, id):
    """The route for this function is called by django-payments after a registration is submitted. """
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

from django.views.generic import ListView, FormView, CreateView, DetailView, UpdateView
from django.views.generic.edit import BaseUpdateView, BaseCreateView, FormMixin, ProcessFormView
from django.views.generic.list import MultipleObjectMixin, MultipleObjectTemplateResponseMixin


class TempCreateView(CreateView):
    content_type = ''
    extra_context = ''
    form_class = ''
    http_method_names = ''
    initial = ''
    prefix = ''
    response_class = ''
    success_url = ''
    template_engine = ''
    template_name = ''

    context_object_name = ''
    fields = ''
    model = ''
    pk_url_kwarg = ''
    queryset = ''
    slug_field = ''
    slug_url_kwarg = ''
    template_name_field = ''
    template_name_suffix = ''

    # unsure how to accuratly call this one
    # def as_view(**initkwargs):
    #     print('================ as_view =================')
    #     return super().as_view(**initkwargs)

    def dispatch(self, *args, **kwargs):
        print('================ dispatch =================')
        return super(TempCreateView, self).dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        print('================ get =================')
        return super(TempCreateView, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        print('================ post =================')
        return super(TempCreateView, self).post(*args, **kwargs)

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
        return super(TempCreateView, self).get_form_kwargs()

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
        return super(TempCreateView, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        print('================ get_template_names =================')
        return super().get_template_names()

    # def form_valid(self, form):
    #     # Inside the following is when the form is called
    #     # to be verified.
    #     # if successful, will return a self.get_success_url
    #     return super(TempCreateView, self).form_valid(form)

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

    def http_method_not_allowed(self, *args, **kwargs):
        print('================ http_method_not_allowed =================')
        return super(TempCreateView, self).http_method_not_allowed(*args, **kwargs)

    def setup(self, *args, **kwargs):
        print('================ setup =================')
        return super(TempCreateView, self).setup(*args, **kwargs)

    def get_context_object_name(self, obj):
        print('================ get_context_object_name =================')
        return super().get_context_object_name(obj)

    def get_queryset(self):
        print('================ get_queryset =================')
        return super().get_queryset()

    def get_slug_field(self):
        print('================ get_slug_field =================')
        return super().get_slug_field()

    # end class TempCreateView


class CreateMany(
    MultipleObjectTemplateResponseMixin,
    FormMixin,
    MultipleObjectMixin,
    ProcessFormView
    ):
    """Sometimes we want to allow the creation of many records/objects.
        Sometimes we will want to edit mulitiple records/objects.
        Sometimes we will want to update or create if they do not exist.
        This is going to be a lot like the default Django UpdateView,
        but will use MultipleObject instead of SingleObject versions of mixins

        CreateView Process we will mimic:
        SingleObjectTemplateResponseMixin => MultipleObjectTemplateResponseMixin
            TemplateResponseMixin
        BaseCreateView:
            ModelFormMixin
                FormMixin
                    ContextMixin
                SingleObjectMixin => MultipleObjectMixin
                    ContextMixin
            ProcessFormView
                View
    """
    from django.core.exceptions import ImproperlyConfigured
    from django.forms import models as model_forms

    object_list = None  # MultipleObjectMixin looks for this
    template_name_suffix = '_form'  # Matches the normal CreateView
    fields = None  # Matches ModelForm Mixin

    def get_form_class(self):  # Matches ModelForm Mixin
        """Return the form class to use in this view."""
        if self.fields is not None and self.form_class:
            raise ImproperlyConfigured(
                "Specifying both 'fields' and 'form_class' is not permitted."
            )
        if self.form_class:
            return self.form_class
        else:
            if self.model is not None:
                # If a model has been explicitly provided, use it
                model = self.model
            elif getattr(self, 'object', None) is not None:
                # If this view is operating on a single object, use
                # the class of that object
                model = self.object.__class__
            else:
                # Try to get a queryset and extract the model class
                # from that
                model = self.get_queryset().model

            if self.fields is None:
                raise ImproperlyConfigured(
                    "Using ModelFormMixin (base class of %s) without "
                    "the 'fields' attribute is prohibited." % self.__class__.__name__
                )

            return model_forms.modelform_factory(model, fields=self.fields)

    def get_form_kwargs(self):  # Matches ModelForm Mixin
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()
        if hasattr(self, 'object'):
            kwargs.update({'instance': self.object})
        return kwargs

    def get_success_url(self):  # Matches ModelForm Mixin
        """Return the URL to redirect to after processing a valid form."""
        if self.success_url:
            url = self.success_url.format(**self.object.__dict__)
        else:
            try:
                url = self.object.get_absolute_url()
            except AttributeError:
                raise ImproperlyConfigured(
                    "No URL to redirect to.  Either provide a url or define"
                    " a get_absolute_url method on the Model.")
        return url

    def form_valid(self, form):  # Matches ModelForm Mixin
        """If the form is valid, save the associated model."""
        self.object = form.save()
        return super().form_valid(form)

    #  end class CreateMany



# USEFUL CODE SNIPPET:
# for attr in dir(Registration):
#     print("self.%s = %r" % (attr, getattr(self, attr)))
#     print('-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-')

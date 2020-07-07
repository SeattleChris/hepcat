from django.contrib import admin
from django.forms import ModelForm, Textarea, ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.conf import settings
from .models import (SiteContent, Resource, Subject, Session, ClassOffer,
                     Profile, Payment, Registration, Location)
from datetime import timedelta

# Register your models here.
# TODO: Make a ResourceAdmin? This could modify which are shown


class ResourceInline(admin.StackedInline):
    """ Admin can add a Resource while on the Subject or ClassOffer add/change form. """
    model = Resource
    extra = 5

    # prepopulated_fields does not allow me to set defaults or initial
    # autocomplete does not allow me to set defaults or initial
    # formfield_overrides ... uh, I think that only changes widgets?
    # exclude = ('classoffer', )
    # get_changeform_initial_data is not for this context.

    # fields = ('CONTENT_RENDER', 'MODEL_CHOICES', 'CONTENT_CHOICES', 'USER_CHOICES',
    #           'PUBLISH_CHOICES', 'id', 'subject', 'classoffer', 'content_type', 'user_type',
    #           'avail', 'expire', 'imagepath', 'filepath', 'link', 'text', 'title',
    #           'description', 'date_added', 'date_modified', 'content_path', 'ct', )
    fieldsets = (
        (None, {
            'fields': (('user_type', 'content_type',), ('avail', 'expire'), ('title', 'description')),
        }),
        ('Data Fields', {
            'classes': ('collapse',),
            'fields': ('imagepath', 'filepath', 'link', 'text',)
        }),
        # ('To Hide', {
        #     'fields': ('related_type', 'subject', 'classoffer', ),
        #     # 'classes': ('hidden', ),
        # }),
    )
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'cols': 60, 'rows': 2})},
    }

    # def get_changeform_initial_data(request):
    #     initial = {}
    #     print('====== ResourceInline . get_changeform_initial_data =====')
    #     return initial

    def get_formset(self, request, obj=None, **kwargs):
        # initial = []
        print('========== ResourceInline.get_formset ================')
        print(self)
        for ea in dir(self):
            print(ea)
        # print(self.parent_model)
        print('----------- Obj -----------')
        print(obj)
        # for ea in dir(obj):
        #     print(ea)
        related, subject, classoffer = '', None, None
        if isinstance(obj, Subject):
            related = 'Subject'
            subject = obj
            classoffer = None
            self.exclude = ('related_type', 'classoffer',)
        elif isinstance(obj, ClassOffer):
            related = 'ClassOffer'
            subject = None
            classoffer = obj
            self.exclude = ('subject',)
        else:
            related = 'Other'
            subject = None
            classoffer = None
            self.exclude = ('subject', 'classoffer', )
        print(f'{related}, subj: {subject}, co: {classoffer}')
        # initial.append({
        #     'related_type': related,
        #     'subject': subject,
        #     'classoffer': classoffer,
        # })
        formset = super(ResourceInline, self).get_formset(request, obj, **kwargs)
        # formset.__init__ = curry(formset.__init__, initial=initial)
        return formset


class SubjectAdmin(admin.ModelAdmin):
    """ Admin change/add for Subjects. Has an inline for Resources. """
    model = Subject
    list_display = ('__str__', 'title', 'level', 'version', )
    list_display_links = ('__str__', 'title')
    inlines = (ResourceInline, )
    # TODO: What if we want to attach an already existing Resource?

    # def get_queryset(self, request):
    #     queryset = super().get_queryset(request)

    #     return queryset


class ClassOfferAdmin(admin.ModelAdmin):
    """ Admin change/add for ClassOffers. Has an inline for Resources. """
    model = Subject
    list_display = ('__str__', 'subject', 'session',)
    # ('subject', 'session', 'teachers', 'class_day', 'start_time',)
    list_display_links = ('__str__',)
    inlines = (ResourceInline, )
    # TODO: What if we want to attach an already existing Resource?

    # def get_queryset(self, request):
    #     queryset = super().get_queryset(request)
    #     return queryset


class AdminSessionForm(ModelForm):
    def clean(self):
        # print("=================== Admin Session Form Clean method ======================")
        data = super().clean()
        key_day = data.get('key_day_date')
        prev_sess = Session.last_session(since=key_day)
        day_shift = data.get('max_day_shift')
        early_day = key_day + timedelta(days=day_shift) if day_shift < 0 else key_day
        if prev_sess and prev_sess.end_date >= early_day:
            message = "Overlapping class dates with those settings. "
            if early_day < key_day:
                message += "You could move the other class days to happen after the main day, "
            else:
                message += "You could "
            message += "add a break week on the previous session, or otherwise change when this session starts. "
            raise ValidationError(_(message))
        if data.get('flip_last_day') and data.get('skip_weeks') == 0:
            message = "Your selection of flipping the last class does not work with your zero skipped weeks input. "
            raise ValidationError(_(message))
        return data


class SessiontAdmin(admin.ModelAdmin):
    """ Admin manage of Session models. New Sessions will populate initial values based on last Session. """
    model = Session
    form = AdminSessionForm
    list_display = ('name', 'start_day', 'end_day', 'publish_day', 'expire_day')
    ordering = ('key_day_date',)
    fields = ('name', ('key_day_date', 'max_day_shift'), 'num_weeks',
              ('skip_weeks', 'flip_last_day'), 'break_weeks', ('publish_date', 'expire_date'))

    def date_with_day(self, obj, field=None):
        """ Will format the obj.field datefield to include the day of the week. """
        date_day = getattr(obj, field, None)
        return date_day.strftime('%A %B %-d, %Y') if date_day else ''  # django template language for date: 'l N j, Y'

    def start_day(self, obj): return self.date_with_day(obj, field='start_date')
    def end_day(self, obj): return self.date_with_day(obj, field='end_date')
    def publish_day(self, obj): return self.date_with_day(obj, field='publish_date')
    def expire_day(self, obj): return self.date_with_day(obj, field='expire_date')
    publish_day.admin_order_field = 'publish_date'
    expire_day.admin_order_field = 'expire_date'


class StudentClassInline(admin.TabularInline):
    """ Admin can attach a class Registration while on the Profile add/change form. """
    model = Registration
    extra = 2


class ProfileAdmin(admin.ModelAdmin):
    """ Admin can modify and view Profiles of all users. """
    model = Profile
    list_display = ['__str__', 'username', 'highest_subject', 'level', 'beg_finished', 'l2_finished']
    list_display_links = ('__str__', 'username')
    filter_horizontal = ('taken',)
    ordering = ('date_modified', 'date_added',)
    inlines = (StudentClassInline, )


class RegistrationAdmin(admin.ModelAdmin):
    """ Admin change/add for Registrations, which are records of what students have signed up for. """
    model = Registration
    list_display = ['first_name', 'last_name', 'credit', 'reg_class', 'paid']
    list_display_links = ['first_name', 'last_name']
    list_filter = ('classoffer__session', 'classoffer__class_day')
    # TODO: add ability to only display the class_day that exist in qs
    # https://docs.djangoproject.com/en/2.1/ref/contrib/admin/ see list_filter
    # TODO: modify so by default it shows current session filter
    ordering = ('-classoffer__class_day', 'classoffer__start_time', 'student__user__first_name')

    # ordering = ('reg_class', )


admin.site.site_header = settings.BUSINESS_NAME + ' Admin'
admin.site.site_title = settings.BUSINESS_NAME + ' Admin'
admin.site.index_title = 'Admin Home'
admin.site.register(Subject, SubjectAdmin)
admin.site.register(ClassOffer, ClassOfferAdmin)
admin.site.register(Session, SessiontAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Registration, RegistrationAdmin)
# For the following: each model in the tuple for the first parameter will use default admin.
admin.site.register((SiteContent, Payment, Location, Resource))

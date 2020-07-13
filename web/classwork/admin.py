from django.contrib import admin
from django.forms import ModelForm, Textarea, ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.conf import settings
from .models import (SiteContent, Resource, Subject, Session, ClassOffer,
                     Profile, Payment, Registration, Location)
# from .helper import date_with_day
from datetime import timedelta


def date_with_day(obj, field=None, short=False, year=False):
    """ Will format the obj.field datefield to include the day of the week. """
    date_day = getattr(obj, field, None)
    date_format = '%a' if short else '%A'
    date_format += ' %B %-d'  # django template language for date: 'l N j'
    date_format += ', %Y' if year else ''  # django template language for date: 'l N j, Y'
    return date_day.strftime(date_format) if date_day else ''

# Register your models here.
# TODO: Make a ResourceAdmin? This could modify which are shown


class ResourceInline(admin.StackedInline):
    """ Admin can add a Resource while on the Subject or ClassOffer add/change form. """
    model = Resource
    extra = 1
    fieldsets = (
        (None, {
            'fields': (('user_type', 'content_type',), ('avail', 'expire'), ('title', 'description')),
        }),
        ('Data: Files, Links, & Text', {
            'classes': ('collapse',),
            'fields': ('imagepath', 'filepath', 'link', 'text',)
        }),
        )
    formfield_overrides = {models.TextField: {'widget': Textarea(attrs={'cols': 60, 'rows': 2})}, }


class SubjectAdmin(admin.ModelAdmin):
    """ Admin change/add for Subjects. Has an inline for Resources. """
    model = Subject
    list_display = ('__str__', 'title', 'level', 'version', )
    list_display_links = ('__str__', 'title')
    inlines = (ResourceInline, )
    # TODO: What if we want to attach an already existing Resource?
    fields = (
        ('level', 'version'),
        'title', 'tagline_1', 'tagline_2', 'tagline_3',
        ('num_weeks', 'num_minutes'),
        'description', 'image',
        ('full_price', 'pre_pay_discount'),
        ('qualifies_as_multi_class_discount', 'multiple_purchase_discount')
    )


class ClassOfferAdmin(admin.ModelAdmin):
    """ Admin change/add for ClassOffers. Has an inline for Resources. """
    model = ClassOffer
    list_display = ('__str__', 'subject', 'session', 'start_day', 'start_time', 'end_day')
    list_display_links = ('__str__',)
    ordering = ('session__key_day_date', '_num_level')
    list_filter = ('session', 'subject', '_num_level', 'class_day')
    inlines = (ResourceInline, )
    fieldsets = (
        (None, {
            'fields': (
                ('subject', 'session',),
                ('location', 'teachers', 'manager_approved'),
                ('class_day', 'start_time')
            ),
        }),
        ('Missed Classes', {
            'classes': ('collapse', ),
            "fields": ('skip_weeks', 'skip_tagline'),
        })
    )

    def start_day(self, obj): return date_with_day(obj, field='start_date')
    def end_day(self, obj): return date_with_day(obj, field='end_date', short=True, year=True)
    start_day.short_description = 'start'
    end_day.short_description = 'end'
    # TODO: What if we want to attach an already existing Resource?


class AdminSessionForm(ModelForm):
    def clean(self):
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
            raise ValidationError(_(message), code='invalid')
        if data.get('flip_last_day') and data.get('skip_weeks') == 0:
            message = "Your selection of flipping the last class does not work with your zero skipped weeks input. "
            raise ValidationError(_(message), code='invalid')
        return data

    def full_clean(self):
        full_clean = super().full_clean()
        if True:  # TODO: Is there a way to only run the following when appropriate?
            instance_after_model_clean = {name: getattr(self.instance, name, None) for name in self.fields}
            data = self.data.copy()
            data.update(instance_after_model_clean)
            self.data = data
        return full_clean


class SessiontAdmin(admin.ModelAdmin):
    """ Admin manage of Session models. New Sessions will populate initial values based on last Session. """
    model = Session
    form = AdminSessionForm
    list_display = ('name', 'start_day', 'end_day', 'skips', 'breaks', 'publish_day', 'expire_day')
    ordering = ('key_day_date',)
    fields = ('name', ('key_day_date', 'max_day_shift'), 'num_weeks',
              ('skip_weeks', 'flip_last_day'), 'break_weeks', ('publish_date', 'expire_date'))

    def start_day(self, obj): return date_with_day(obj, field='start_date')
    def end_day(self, obj): return date_with_day(obj, field='end_date')
    def publish_day(self, obj): return date_with_day(obj, field='publish_date')
    def expire_day(self, obj): return date_with_day(obj, field='expire_date')
    def skips(self, obj): return getattr(obj, 'skip_weeks', None)
    def breaks(self, obj): return getattr(obj, 'break_weeks', None)
    publish_day.admin_order_field = 'publish_date'
    expire_day.admin_order_field = 'expire_date'
    skips.short_description = 'skips'
    breaks.short_description = 'breaks'


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

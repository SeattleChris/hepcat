from django.contrib import admin
from django.forms import ModelForm, Textarea, ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.conf import settings
from .models import (SiteContent, Resource, Subject, Session, ClassOffer,
                     Staff, Student, Payment, Registration, Location)
# from .helper import date_with_day
from datetime import timedelta, time, datetime as dt


def date_with_day(obj, field=None, short=False, year=False):
    """ Will format the obj.field datefield to include the day of the week. """
    date_day = getattr(obj, field, None)
    date_format = '%a' if short else '%A'
    date_format += ' %B %-d'  # django template language for date: 'l N j'
    date_format += ', %Y' if year else ''  # django template language for date: 'l N j, Y'
    return date_day.strftime(date_format) if date_day else ''


class ClassDayListFilter(admin.SimpleListFilter):
    title = _('class day')   # Human-readable title used in the filter sidebar
    parameter_name = 'class_day_filter'  # Parameter for the filter that will be used in the URL query.

    def lookups(self, request, model_admin):
        """ Returns a list of tuples. The first tuple element is the coded value, second element is the label. """
        qs = model_admin.get_queryset(request)
        field_key = 'class_day'
        if isinstance(model_admin, RegistrationAdmin):
            field_key = 'classoffer__' + field_key
        print(field_key)
        for value, label in ClassOffer.DOW_CHOICES:
            if qs.filter(**{field_key: value}).exists():
                yield (value, label)

    def queryset(self, request, queryset):
        """ Returns the filtered queryset based on value provided in the query string, retrievable via self.value(). """
        # Compare the requested value to decide how to filter the queryset.
        field_key = 'class_day'
        if queryset.model == Registration:
            field_key = 'classoffer__' + field_key
        return queryset.filter(**{field_key: self.value()}) if self.value() else queryset


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
    # TODO: Modify which are shown
    formfield_overrides = {models.TextField: {'widget': Textarea(attrs={'cols': 60, 'rows': 2})}, }


class StudentClassInline(admin.TabularInline):
    """ Admin can attach a class Registration while on the Student profile add/change form. """
    model = Registration
    extra = 2

# Register your models here.


class SubjectAdmin(admin.ModelAdmin):
    """ Admin change/add for Subjects. Has an inline for Resources. """
    model = Subject
    list_display = ('__str__', 'title', 'level_num', 'level', 'version', )
    list_display_links = ('__str__', 'title', )
    list_filter = ('level_num', 'level', )
    inlines = (ResourceInline, )
    # TODO: What if we want to attach an already existing Resource?
    fields = (
        ('level', 'version', 'level_num'),
        'title', 'tagline_1', 'tagline_2', 'tagline_3',
        ('num_weeks', 'num_minutes'),
        'description', 'image',
        ('full_price', 'pre_pay_discount'),
        ('qualifies_as_multi_class_discount', 'multiple_purchase_discount'),
    )

    # TODO: Look into ModelAdmin asset definitions
    # class Media:
    #     css = {
    #         "all": ("my_styles.css",)
    #     }
    #     js = ("my_code.js",)


class ClassOfferAdmin(admin.ModelAdmin):
    """ Admin change/add for ClassOffers. Has an inline for Resources. """
    model = ClassOffer
    list_display = ('__str__', 'subject', 'session', 'time', 'start_day', 'end_day', )
    list_display_links = ('__str__', )
    list_filter = ('session', 'subject', '_num_level', ClassDayListFilter, )
    ordering = ('session__key_day_date', '_num_level', )
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
        }),
    )

    def time(self, obj):
        """ Returns a string for the duration between the start and end time, or 'Not Set' if missing needed data.
            Input: 'obj' -> ClassOffer instance.
            Output -> string:
                "Not Set" if missing values for obj.start_time or obj.subject.num_minutes.
                "7pm - 8pm" if start time was 7pm and duration was 60 minutes, and similar if both times on the hour.
                "10:00am - 11:30am" if start at 10am & duration 90 minutes, and similar if either ends not on the hour.
        """
        start = getattr(obj, 'start_time', None)
        num_minutes = getattr(obj.subject, 'num_minutes', None)
        if not isinstance(start, time) or not num_minutes:
            return "Not Set"
        time_format = '%I%p' if start.minute == 0 and num_minutes % 60 == 0 else '%I:%M%p'
        temp = dt(1930, 1, 1, start.hour, start.minute) + timedelta(minutes=num_minutes)
        end = temp.time()
        formatted_time_list = [t.strftime(time_format).strip('0').lower() for t in (start, end)]
        return ' - '.join(formatted_time_list)

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
        # The following condition does not occur because it has already been corrected in Session.clean()
        # if data.get('flip_last_day') and data.get('skip_weeks') == 0:
        #     message = "Your selection of flipping the last class does not work with your zero skipped weeks input. "
        #     raise ValidationError(_(message), code='invalid')
        return data

    def full_clean(self):
        """ Extended functionality with repopulating the form with data updated by the model's clean method. """
        full_clean = super().full_clean()
        if True:  # TODO: Is there a way to only run the following when appropriate?
            instance_after_model_clean = {name: getattr(self.instance, name, None) for name in self.fields}
            data = self.data.copy()
            data.update(instance_after_model_clean)
            # TODO: Should data be cast to a QueryDict to maintain immutable quality?
            self.data = data
        return full_clean


class SessiontAdmin(admin.ModelAdmin):
    """ Admin manage of Session models. New Sessions will populate initial values based on last Session. """
    model = Session
    form = AdminSessionForm
    list_display = ('name', 'start_day', 'end_day', 'skips', 'breaks', 'publish_day', 'expire_day', )
    ordering = ('key_day_date', )
    fields = ('name', ('key_day_date', 'max_day_shift'), 'num_weeks',
              ('skip_weeks', 'flip_last_day'), 'break_weeks', ('publish_date', 'expire_date'), )

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


class StaffAdmin(admin.ModelAdmin):
    """ Admin can modify and view Staff user profiles. """
    model = Staff
    list_display = ('__str__', 'username', 'listing', 'bio_done', 'tax', )
    list_display_links = ('__str__', 'username', )
    # TODO: Allow listing to be editable on Admin list view.
    list_filter = ('user__is_staff', 'user__is_active', )
    ordering = ('date_modified', 'date_added', )
    fields = (('user', 'listing', 'tax_doc'), 'bio', )

    def bio_done(self, obj): return True if len(obj.bio) > 0 else False
    def tax(self, obj): return True if len(obj.tax_doc) > 0 else False
    bio_done.boolean = True
    tax.boolean = True


class StudentAdmin(admin.ModelAdmin):
    """ Admin can modify and view Student user profiles. """
    model = Student
    list_display = ('__str__', 'username', 'max_subject', 'max_level', 'level', 'beg_done', 'l2_done', 'l3_done', )
    list_display_links = ('__str__', 'username', )
    list_filter = ('user__is_staff', 'taken__session', 'taken__subject__level', 'level', )    # , 'taken__subject',
    list_select_related = True
    ordering = ('date_modified', 'date_added', )
    # filter_horizontal = ('taken',)
    inlines = (StudentClassInline, )
    fields = (('user', 'level', 'credit'), 'bio', )

    def max_subject(self, obj): return list(obj.highest_subject.get('subjects', ['Unknown']))
    def max_level(self, obj): return obj.highest_subject.get('level_num__max', 0)
    def beg_done(self, obj): return obj.beg.get('done')
    def l2_done(self, obj): return obj.l2.get('done')
    def l3_done(self, obj): return obj.l3.get('done')
    beg_done.boolean = True
    l2_done.boolean = True
    l3_done.boolean = True

    # def message_user(self, request, message, level=messages.INFO, extra_tags='', fail_silently=False):
    #     # TODO: Look into ModelAdmin.message_user
    #     return super().message_user(request, message, level=level, extra_tags=extra_tags, fail_silently=fail_silently)


class RegistrationAdmin(admin.ModelAdmin):
    """ Admin change/add for Registrations, which are records of what students have signed up for. """
    model = Registration
    list_display = ('first_name', 'last_name', 'credit', 'reg_class', 'paid', )
    list_display_links = ('first_name', 'last_name', )
    list_filter = ('classoffer__session', ClassDayListFilter, )  # 'classoffer__class_day',
    ordering = ('-classoffer__class_day', 'classoffer__start_time', 'student__user__first_name', )
    # TODO: modify so by default it shows current session filter


admin.site.site_header = settings.BUSINESS_NAME + ' Admin'
admin.site.site_title = settings.BUSINESS_NAME + ' Admin'
admin.site.index_title = 'Admin Home'
admin.site.register(Subject, SubjectAdmin)
admin.site.register(ClassOffer, ClassOfferAdmin)
admin.site.register(Session, SessiontAdmin)
admin.site.register(Staff, StaffAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Registration, RegistrationAdmin)
# For the following: each model in the tuple for the first parameter will use default admin.
admin.site.register((SiteContent, Payment, Location, Resource))

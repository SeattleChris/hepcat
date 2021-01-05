from django.db import models
from django.db.models import Q, F, Func, Case, When, Count, Max, OuterRef, DateField, ExpressionWrapper as EW
# , Avg, Sum, Min, Value, Subquery
from django.db.models.functions import Least, Extract  # , ExtractWeek, ExtractIsoYear, Trunc, Now,
# from .transforms import AddDate, DateDiff, DayYear, NumDay, DateFromNum, MakeDate, DateToday
# from django.contrib.admin.views.decorators import staff_member_required  # TODO: Add decorator to needed views.
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.core.mail import EmailMessage
from django.conf import settings
from django.urls import reverse
from django_countries.fields import CountryField
from decimal import Decimal  # used for Payments
from payments import PurchasedItem
from payments.models import BasePayment
from datetime import date, timedelta, datetime as dt

# TODO: Implement calling resource_filepath for resource uploads.
# TODO: Add @staff_member_required decorator to admin views?
# Create your models here.


class SiteContent(models.Model):
    """Public content for different sections of the site. """
    # id = auto-created
    name = models.CharField(max_length=120, help_text=_('Descriptive name used to find this content'))
    text = models.TextField(blank=True, help_text=_('Text content used in page or email publication'))

    date_added = models.DateField(auto_now_add=True, )
    date_modified = models.DateField(auto_now=True, )

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<SiteContent: {} >'.format(self.name)


class Location(models.Model):
    """This stores information about each location where ClassOffers may be held. """
    # TODO: Should we add a publish flag in the DB for each location?
    # id = auto-created
    name = models.CharField(max_length=120, )
    code = models.CharField(max_length=120, )
    address = models.CharField(max_length=191, )
    city = models.CharField(max_length=120, default=settings.DEFAULT_CITY, )
    state = models.CharField(max_length=63, default=settings.DEFAULT_COUNTRY_AREA_STATE, )
    zipcode = models.CharField(max_length=15, )
    map_link = models.URLField(_("Map Link"), blank=True, )

    date_added = models.DateField(auto_now_add=True, )
    date_modified = models.DateField(auto_now=True, )

    def get_absolute_url(self):
        return reverse('location_detail', args=[str(self.id)])

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Location: {} | Link: {} >'.format(self.name, self.map_link)


class ResourceManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset()

    def live(self, start=None, end=None, skips=0, type_user=0, **kwargs):
        """Will filter and annotate to return only currently published Resource for the given context. """
        raise NotImplementedError


class Resource(models.Model):
    """Subjects and ClassOffers can have various resources released to the students at
        different times while attending a ClassOffer or after they have completed the session.
        Subjects and ClassOffers can have various resources available to the instructors
        to aid them in class preperation and presentation.
    """
    # TODO: Make validation checks on new Resource instances
    # TODO: does it require an admin/teacher response before released?
    # TODO: Add sending email feature.

    CONTENT_CHOICES = (
        ('url', _('External Link')),
        ('file', _('Formatted Text File')),
        ('text', _('Plain Text')),
        ('video', _('Video file on our site')),
        ('image', _('Image file on our site')),
        ('link', _('Webpage on our site')),
        ('email', _('Email file')))
    USER_CHOICES = (
        (0, _('Public')),
        (1, _('Student')),
        (2, _('Teacher')),
        (3, _('Admin')),)
    PUBLISH_CHOICES = (
        (0, _('On Sign-up, before starting')),
        *[(num, _('After class {}'.format(num))) for num in range(1, settings.SESSION_MAX_WEEKS)],
        (200, _('After completion')))

    # id = auto-created
    subjects = models.ManyToManyField('Subject', related_name='resources', blank=True, )
    classoffers = models.ManyToManyField('ClassOffer', related_name='resources', blank=True, )
    content_type = models.CharField(max_length=15, choices=CONTENT_CHOICES, )
    user_type = models.PositiveSmallIntegerField(default=1, choices=USER_CHOICES, help_text=_('Who is this for?'), )
    avail = models.PositiveSmallIntegerField(default=0, choices=PUBLISH_CHOICES,
                                             help_text=_('When is this resource available?'), )
    expire = models.PositiveSmallIntegerField(default=0, help_text=_('Number of published weeks? (0 for always)'), )
    imagepath = models.ImageField(upload_to='resource/', help_text=_('If an image, upload here'), blank=True, )
    filepath = models.FileField(upload_to='resource/', help_text=_('If a file, upload here'), blank=True, )
    link = models.URLField(max_length=191, help_text=_('External or Internal links go here'), blank=True, )
    text = models.TextField(_("Text Content"), help_text=_('Content used in page or email publication'), blank=True, )
    name = models.CharField(max_length=60, )
    description = models.TextField(_("Staff Notes Description"), help_text=_("Only used as staff notes"), blank=True, )

    date_added = models.DateField(auto_now_add=True, )
    date_modified = models.DateField(auto_now=True, )
    objects = ResourceManager()

    # def respath(self):
    #     """Returns the data field for the selected content type"""
    #     content_path = {
    #         'url': self.link,
    #         'file': self.filepath,
    #         'text': self.text,
    #         'video': self.filepath,
    #         'image': self.imagepath,
    #         'link': self.link,
    #         'email': self.text
    #     }
    #     return content_path[self.content_type]

    def get_absolute_url(self):
        return reverse('resource_detail', args=[str(self.id)])

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Resource: {} | Type: {} >'.format(self.name, self.content_type)


class Subject(models.Model):
    """A 'Subject' is the general information and teaching content intended to be covered. The details of what was
        actually covered are part of a 'ClassOffer', which also includes details of when, where, etc it occurs.
    """
    LEVEL_CHOICES = (
        ('Beg', _('Beginning')),
        ('L2', _('Lindy 2')),
        # These first two must represent the Beginning and Level 2 class series.
        ('L3', _('Lindy 3')),
        ('Spec', _('Special Focus')),
        ('WS', _('Workshop')),
        ('Priv', _('Private Lesson')),
        ('PrivSet', _('Private - Multiple Lessons')),
        ('Other', _('Other')))
    LEVEL_ORDER = {
        'Beg': 1,
        'L2': 2,
        'WS': 2.5,
        'L3': 3,
        'Spec': 3.5,
        'L4': 4, }
    # TODO: Update so that site Admin can change class level logic.
    VERSION_CHOICES = (
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('N', 'NA'), )

    # id = auto-created
    level = models.CharField(max_length=8, default='Spec', choices=LEVEL_CHOICES, )
    level_num = models.DecimalField(max_digits=3, decimal_places=1, default=0,  # LEVEL_ORDER.get(level.default, 0)
                                    help_text=_("Will be computed if left blank. "), blank=True, )
    version = models.CharField(max_length=1, choices=VERSION_CHOICES, )
    name = models.CharField(max_length=125, default=_('Untitled'), )
    tagline_1 = models.CharField(max_length=23, blank=True, )
    tagline_2 = models.CharField(max_length=23, blank=True, )
    tagline_3 = models.CharField(max_length=23, blank=True, )
    num_weeks = models.PositiveSmallIntegerField(default=settings.DEFAULT_SESSION_WEEKS, )
    num_minutes = models.PositiveSmallIntegerField(default=settings.DEFAULT_CLASS_MINUTES, )
    description = models.TextField()
    # TODO: Do we want some ForeignKey references for some common Resources:
    # syllabus, teacher_plan, weekly emails and videos, etc.
    image = models.URLField(max_length=191, blank=True, )
    # TODO: Update to using ImageField. But what if we want existing image?
    # image = models.ImageField(upload_to=MEDIA_ROOT)
    full_price = models.DecimalField(max_digits=6, decimal_places=2, default=settings.DEFAULT_CLASS_PRICE, )
    pre_pay_discount = models.DecimalField(max_digits=6, decimal_places=2, default=settings.DEFAULT_PRE_DISCOUNT, )
    multiple_purchase_discount = models.DecimalField(max_digits=6, decimal_places=2, default=settings.MULTI_DISCOUNT, )
    qualifies_as_multi_class_discount = models.BooleanField(default=True, )
    # resources exists from ManyToMany from Resource
    date_added = models.DateField(auto_now_add=True, )
    date_modified = models.DateField(auto_now=True, )

    def compute_level_num(self, level_value=None, set_self=True):
        """Translate and assign the number associated to the value in 'level' field, assigning 0 if not determined. """
        level_value = level_value if level_value is not None else self.level
        num = self.LEVEL_ORDER.get(level_value, 0)
        if set_self:
            self.level_num = num
        return num

    @property
    def _str_slug(self):
        slug = str(self.level) + str(self.version)
        common_levels = [code for code, display in self.LEVEL_CHOICES[:int(settings.COMMON_LEVELS_COUNT)]]
        if self.level not in common_levels:
            slug += ': {}'.format(self.name)
        return slug

    def save(self, *args, **kwargs):
        if not self.level_num:
            self.compute_level_num()
        super().save(*args, **kwargs)

    def __str__(self):
        return self._str_slug

    def __repr__(self):
        return '<Subject: {} | Level: {} | Version: {} >'.format(self.name, self.level, self.version)


# class LevelGroup(models.Model):
#     """Sometimes there will be multiple Subjects (classes)
#         that, as a group, are meant to be taken before
#         a student has completed that Subject.
#     """
#     # id = auto-created
#     name = models.CharField(max_length=8, choices=Subject.LEVEL_CHOICES, default='Spec')
#     # collection = models.ManyToManyField('Subject', symmetrical=True)
#     collection = models.ForeignKey('Subject', on_delete=models.CASCADE)


def default_publish(): return Session._default_date('publish_date')


def default_key_day(): return Session._default_date('key_day_date')


class Session(models.Model):
    """Classes are offered and published according to which session they belong.
        Each session start date is computed based on 'key_day_date' and the earliest class day.
        - If 'max_day_shift' is zero or positive, the earliest day will be the 'key_day_date'.
        - If 'max_day_shift' is negative, then earliest day is that many days before 'key_day_date.
        Each session may have a determined break number of weeks after the session ends.
        Each session can have some class days that may skip a week of classes (holiday, or other reasons).
        Due to skipped weeks, this can change which day of the week is the last day of classes.
        - Most critically, this can change what is the earliest day the next session can start.
        Each session end date is computed based on all of these values.
        A default value for 'key_day_date' and 'publish_date' are determined based on existing sessions.
        If not manually set, the 'expire_date' will typically set to after the second week of all class days.
        If a session is only three weeks or shorter, it will be treated differently than other sessions.
            - The 'expire_date' will be two days after all possible first class days.
            - Later sessions will skip to previous session for determining computed values.
    """
    # id = auto-created
    name = models.CharField(max_length=15, )
    key_day_date = models.DateField(_('main class start date'), default=default_key_day, )
    max_day_shift = models.SmallIntegerField(
        _('number of days other classes are away from main class'),
        help_text=_('Use negative numbers if others are before the main class day.'),
        default=settings.DEFAULT_MAX_DAY_SHIFT, )
    num_weeks = models.PositiveSmallIntegerField(_('number of class weeks'), default=settings.DEFAULT_SESSION_WEEKS, )
    skip_weeks = models.PositiveSmallIntegerField(_('skipped mid-session class weeks'), default=0, )
    flip_last_day = models.BooleanField(
        _('due to skipped weeks, does the session ending switch between a non-key vs key day?'),
        help_text=_('Possibly true if the skipped class is not on the day that normally is the end of the session.'),
        default=False, )
    break_weeks = models.PositiveSmallIntegerField(_('break weeks after this session'), default=0, )
    publish_date = models.DateField(default=default_publish, blank=True, )
    expire_date = models.DateField(help_text=_('If blank, this will be computed'), blank=True, )

    date_added = models.DateField(auto_now_add=True, )
    date_modified = models.DateField(auto_now=True, )

    @property
    def start_date(self):
        """Return the date for the earliest possible first class day, based on Session field values. """
        first_date = self.key_day_date
        if self.max_day_shift < 0:
            first_date += timedelta(days=self.max_day_shift)
        return first_date

    @property
    def end_date(self):
        """Return the date for the last possible class day, based on Session field values. """
        last_date = self.key_day_date + timedelta(days=7*(self.num_weeks + self.skip_weeks - 1))
        if (self.max_day_shift < 0 and self.flip_last_day) or \
           (self.max_day_shift > 0 and not self.flip_last_day):
            # A) Early non-key day has skipped to end; B) Non-key day came after, and skipped weeks hasn't changed that.
            last_date += timedelta(days=self.max_day_shift)
        return last_date

    @property
    def prev_session(self):
        """Return the Session that comes before the current Session, or 'None' if none exists. """
        return self.last_session(since=self.key_day_date)

    @property
    def next_session(self):
        """Returns the Session that comes after the current Session, or 'None' if none exists. """
        key_day = self.key_day_date
        key_day = key_day() if callable(key_day) else key_day
        key_day = key_day.isoformat() if isinstance(key_day, (date, dt)) else key_day
        later = Session.objects.filter(key_day_date__gt=key_day)
        # next_one_or_none = later.order_by('key_day_date').first()
        try:
            next_sess = later.filter(num_weeks__gt=settings.SESSION_LOW_WEEKS).earliest('key_day_date')
        except self.DoesNotExist:
            next_sess = None
        return next_sess

    @classmethod
    def last_session(cls, since=None):
        """Returns the Session starting the latest, or latest prior to given 'since' date. Return None if none. """
        query = cls.objects
        if since:
            # TODO: Check isinstance an appropriate datetime obj
            query = query.filter(key_day_date__lt=since)
        try:
            result = query.latest('key_day_date')  # .order_by('-key_day_date').first()
        except cls.DoesNotExist:
            result = None
        return result

    @classmethod
    def _default_date(cls, field, since=None):
        """Compute a default value for 'key_day_date' or 'publish_date' field. """
        allowed_fields = ('key_day_date', 'publish_date')
        if field not in allowed_fields:
            raise ValueError(_("Not a valid field parameter: {} ".format(field)))
        now = date.today()
        new_date = None
        final_session = cls.last_session(since=since)
        while final_session is not None and final_session.num_weeks < settings.SESSION_LOW_WEEKS:
            final_session = final_session.prev_session
        if not final_session:
            new_date = None
        elif field == 'key_day_date':
            known_weeks = final_session.num_weeks + final_session.skip_weeks + final_session.break_weeks
            later = final_session.max_day_shift > 0
            if final_session.skip_weeks > 0 and \
               ((final_session.flip_last_day and not later) or (later and not final_session.flip_last_day)):
                known_weeks -= 1  # One fewer skips since key day class did not have critical skip_weeks
            new_date = final_session.key_day_date + timedelta(days=7*known_weeks)
        elif field == 'publish_date':
            new_date = getattr(final_session, 'expire_date', None)
        # return new_date.isoformat() if isinstance(new_date, (date, dt)) else date.today().isoformat()
        return new_date or now

    def computed_expire_day(self, key_day=None):
        """Assumes unaffected by skipped weeks. Based on parameters from settings. """
        minimum_session_weeks = settings.SESSION_LOW_WEEKS
        default_expire = settings.DEFAULT_SESSION_EXPIRE
        short_expire = settings.SHORT_SESSION_EXPIRE
        if not key_day:
            key_day = self.key_day_date
        adj = self.max_day_shift if self.max_day_shift > 0 else 0
        adj += default_expire if self.num_weeks > minimum_session_weeks else short_expire
        expire = key_day + timedelta(days=adj)
        return expire

    def clean(self):
        """Modifies values for validity checks and if needed to avoid overlapping published Sessions.
            If avoiding overlaps, the publish_date and expire_date are overwritten by determined values.
            May modify a previous Session value for break_weeks, but not any other values.
        """
        key_day = self.key_day_date
        prev_sess = Session.last_session(since=key_day)
        early_day = key_day + timedelta(days=self.max_day_shift) if self.max_day_shift < 0 else key_day
        week = timedelta(days=7)
        # TODO: Check the logic and possible backup solutions
        while prev_sess and prev_sess.end_date >= early_day:
            # If overlap is fixed by moving the pre-key day classes to come after key day, then do it!
            if early_day < self.key_day_date and early_day + week > prev_sess.end_date:
                self.max_day_shift = self.max_day_shift + 7  # Move the extra days come after the key day.
                early_day = key_day
                if self.flip_last_day and self.skip_weeks > 0:
                    self.flip_last_day = False  # Skip day was/is on non-key day, but now it is the natural last_day.
                elif self.skip_weeks > 0:
                    pass  # Skip day was on key_day, possibly others also. So uncertain if flip_last_day should change.
            else:  # Move all current days a week later and record an extra break week for the previous session.
                early_day += week
                key_day += week
                temp_sess = Session.last_session(since=(key_day + timedelta(days=1)))
                if temp_sess == prev_sess:
                    self.key_day_date = key_day
                    prev_sess.break_weeks += 1
                    prev_sess.save(update_fields=['break_weeks'])
                else:
                    prev_sess = temp_sess
                    date_check = prev_sess.key_day_date + timedelta(days=1)
                    key_day = self._default_date('key_day_date', since=date_check)
                    early_day = key_day + timedelta(days=self.max_day_shift) if self.max_day_shift < 0 else key_day
                    self.key_day_date = key_day
                    self.publish_date = prev_sess.expire_date
                    self.expire_date = self.computed_expire_day(key_day=key_day)
        if self.skip_weeks == 0:
            self.flip_last_day = False
        return super().clean()

    def clean_fields(self, exclude=None):
        fix_callables = {'key_day_date', 'publish_date'}
        fix_callables = fix_callables - set(exclude) if exclude else fix_callables
        for field_to_clean in fix_callables:
            field = getattr(self, field_to_clean, None)
            field = field() if callable(field) else field
            setattr(self, field_to_clean, field)
        return super().clean_fields(exclude=exclude)

    def save(self, *args, with_clean=False, **kwargs):
        """If given an 'update_fields' list of field names, directly saves if doing so won't break expire_date.
            Otherwise, which clean methods are used depends on 'with_clean'.
            The 'expire_date' field will be determined if it is not set (recommend).
            If there is a next Session, it will have its publish_date modified to match this session's expire_date.
        """
        if 'update_fields' in kwargs:
            if not all(['expire_date' in kwargs['update_fields'], self.expire_date is None]):
                return super().save(*args, **kwargs)
        exclude = kwargs.get('exclude', None)
        if with_clean:
            self.full_clean(exclude=exclude)
        else:
            self.clean_fields(exclude=exclude)
        if not self.expire_date:
            self.expire_date = self.computed_expire_day(key_day=self.key_day_date)
        next_sess = self.next_session
        if next_sess:
            next_sess.publish_date = self.expire_date
            next_sess.save(update_fields=['publish_date'])
        # try: self.objects.get_next_by_key_day_date().update(publish_date=self.expire_date)
        # except Session.DoesNotExist as e: print(f"There is no next session: {e} ")
        super().save(*args, **kwargs)

    def get_admin_absolute_url(self):
        return reverse('checkin_session', args=[str(self)])

    def get_absolute_url(self):
        return reverse('classoffer_display_session', args=[str(self)])

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Session: {} >'.format(self.name)


class CustomQuerySet(models.QuerySet):

    def with_dates(self):
        return self.annotate(
                dif=Case(
                    When(Q(session__key_day_date__week_day=1),  # On the DB Sunday is 1, but is 6 in Python.
                         then=EW(
                            F('class_day') + 2 - 7 - Extract('session__key_day_date', 'week_day'),
                            output_field=models.SmallIntegerField())),
                    default=EW(
                        F('class_day') + 2 - Extract('session__key_day_date', 'week_day'),
                        output_field=models.SmallIntegerField()),
                    output_field=models.SmallIntegerField()),
            ).annotate(
                shifted=Case(
                    When(dif=0, then=0),
                    When(Q(session__max_day_shift__lt=0) & Q(session__max_day_shift__gt=F('dif')), then=F('dif')+7),
                    When(Q(session__max_day_shift__gt=F('dif')+7), then=F('dif')+7),
                    When(session__max_day_shift__lt=F('dif')-7, then=F('dif')-7),
                    When(Q(session__max_day_shift__gt=0) & Q(session__max_day_shift__lt=F('dif')), then=F('dif')-7),
                    default=F('dif'), output_field=models.SmallIntegerField()),
            ).annotate(
                start_date=Func(F('session__key_day_date'), F('shifted'), function='ADDDATE', output_field=DateField()),
            ).annotate(
                end_date=Func(F('start_date'), 7 * (F('session__num_weeks') - 1 + F('skip_weeks')), function='ADDDATE',
                              output_field=DateField()),
            ).select_related()

    def prepare_get_resources_params(self, **kwargs):
        qs = Resource.objects
        start, end, skips, type_user, max_weeks = None, None, None, None, None
        model = kwargs.pop('model', None)
        if model:
            start = getattr(model, 'start_date', None)
            end = getattr(model, 'end_date', None)
            if start is None or end is None:
                model = ClassOffer.objects.filter(id=model.id).first()
                start = getattr(model, 'start_date', None)
                end = getattr(model, 'end_date', None)
            skips = model.skip_weeks
            max_weeks = getattr(getattr(model, 'session', object), 'num_weeks', None)
            qs = qs.filter(Q(classoffers__id=model.pk) | Q(subjects=model.subject))
            qs = qs.order_by('pk').distinct()
        else:
            start = kwargs.pop('start', None)
            end = kwargs.pop('end', None)
            skips = kwargs.pop('skips', None)
            max_weeks = kwargs.pop('max_weeks', None)
        user = kwargs.pop('user', None)
        if user:
            student = user if isinstance(user, Student) else None
            user = user.user if isinstance(user, (Student, Staff)) else user
            user_val, user_roles = user.user_roles
            type_user = 3 if user_val >= 4 else user_val
            if student:
                pass
        else:
            type_user = kwargs.pop('type_user', 0)
        # TODO: filter for user_type__lt=type_user
        if not model and self.model == ClassOffer:
            start = start or OuterRef('start_date')
            end = end or OuterRef('end_date')
            skips = skips if skips is not None else OuterRef('skip_weeks')
            qs = qs.filter(Q(classoffers__id=OuterRef('pk')) | Q(subjects=OuterRef('subject')))
            qs = qs.order_by('pk').distinct()

        if not isinstance(start, (date, OuterRef)) or not isinstance(end, (date, OuterRef)):
            raise TypeError(_("Both start and end parameters must be date objects or OuterRefs to DateFields. "))
        if not isinstance(skips, (int, OuterRef)):
            raise TypeError(_("The skips parameter must be an integer or an OuterRef to an appropriate field type. "))
        if isinstance(type_user, str):
            user_lookup = {'public': 0, 'student': 1, 'teacher': 2, 'admin': 3, }
            type_user = user_lookup.get(type_user, len(Resource.USER_CHOICES))
        if not isinstance(type_user, int) or type_user < 0 or type_user > len(Resource.USER_CHOICES) - 1:
            raise TypeError(_("The type_user parameter must be an appropriate string or integer"))
        # now = kwargs('check_date', None)
        max_weeks = settings.SESSION_MAX_WEEKS if max_weeks is None else max_weeks
        return (qs, start, end, skips, int(max_weeks), kwargs)

    def get_resources(self, live=False, **kwargs):
        """Returns a filtered & annotated queryset of Resources connected to the current ClassOffer queryset.
            False: Unless over-ridden by later processing of this queryset, it will be ordered with most recent first.
            Filter these results by 'live=True' to get only currently published, and not expired, results.
            Distinct resources, across ClassOffers, requires '.values()' that does not include these annotations.
        """

        res_qs, start, end, skips, max_weeks, kwargs = self.prepare_get_resources_params(**kwargs)
        now = Func(function='CURDATE', output_field=models.DateField())  # TODO: decide CURDATE or UTC_DATE
        dates = [Least(start, now)]
        dates += [Func(start, 7 * i, function='ADDDATE', output_field=models.DateField()) for i in range(max_weeks - 1)]
        # dates += [Func(start, 7 * i, function='ADDDATE') for i in range(max_weeks - 1)]
        # MySQL Functions: ADDDATE, DATEDIFF, DAYOFYEAR, TO_DAYS, FROM_DAYS, MAKEDATE, CURDATE
        res_qs = res_qs.annotate(
                publish=Case(
                    *[When(Q(avail=num), then=date) for num, date in enumerate(dates)],
                    default=end,  # Uses default if 'after class ends' was selected option (value = 200).
                    output_field=models.DateField()),
                days_since=Func(now, start, function='DATEDIFF', output_field=models.IntegerField()),
            ).annotate(
                expire_date=Case(
                    When(Q(expire=0), then=None),
                    default=Func(F('publish'), 7 * (F('expire') + skips),
                                 function='ADDDATE', output_field=models.DateField()),
                    output_field=models.DateField()),
                live=Case(
                    When(Q(publish__gt=now), then=False),
                    When(Q(expire=0), then=True),
                    When(Q(avail__gt=max_weeks), then=Q(days_since__lte=7*(max_weeks + F('expire') + skips - 1))),
                    When(Q(avail=0) & Q(days_since__lte=7*(F('expire') + skips)), then=True),  # avail=0|1 same result
                    When(Q(days_since__lte=7*(F('avail') + F('expire') + skips - 1)), then=True),
                    default=False,
                    output_field=models.BooleanField()),
            )
        # tmp = None if isinstance(end, OuterRef) else res_qs.values('publish', 'days_since', 'live', 'avail', 'expire')
        # if tmp and any(ea.get('avail', 0) == 3 for ea in tmp):
        #     print("============================ GET RESOURCES ANNOTATE ===============================")
        #     print(start)
        #     print(tmp)
        # #    ).order_by('-publish')  # Most recent first. May be overridden later, depending on how this data is used.
        if live:
            res_qs = res_qs.filter(live=True)
        elif kwargs.get('live_by_date', None):
            res_qs = res_qs.filter(
                Q(expire_date__isnull=True) | Q(expire_date__gte=now),
                publish__lte=now
            )
        return res_qs

    def resources(self, **kwargs):
        """Return a queryset.values() of Resource objects that are alive and connected to the current queryset. """
        resource_fields = ('name', 'id', 'content_type', )  # , 'imagepath',
        kwargs['live'] = True  # Calling resources will always only return currently available resources.
        # kwargs.setdefault('live', True)  # unless set False in kwargs, will only return currently available resources.
        arr = [self.get_resources(model=ea, **kwargs).order_by().values(*resource_fields) for ea in self.all()]
        # TODO: Look into 'defer' as a query option instead of 'values' to have a qs of models instead of dicts.
        if len(arr):
            collected = arr[0].union(*arr[1:])
        else:
            collected = Resource.objects.none().values()
        return collected

    def most_recent_resource_per_classoffer(self):
        """This feature is not yet implemented correctly. """
        # res = self.get_resources(
        #         start=OuterRef('start_date'),
        #         end=OuterRef('end_date'),
        #         skips=OuterRef('skip_weeks')
        #     )
        # try:
        #     result = self.annotate(
        #             recent_resource=Subquery(res.values('name')[:1]),
        #         )
        #     print(result)
        # except Exception as e:
        #     print("Exception in ClassOffer manager method: most_recent_resource_per_classoffer ")
        #     print(e)
        raise NotImplementedError
        # return result


class ClassOfferManager(models.Manager):
    def get_queryset(self): return CustomQuerySet(self.model, using=self._db).with_dates()
    def get_resources(self, **kwargs): return self.get_queryset().get_resources(**kwargs)
    def resources(self, **kwargs): return self.get_queryset().resources(**kwargs)
    def most_recent_resource_per_classoffer(self): return self.get_queryset().most_recent_resource_per_classoffer()
    # TODO: If all the methods are just querysets, then refactor to use CustomQuerySet as manager.


class ClassOffer(models.Model):
    """Different classes can be offered at different times and scheduled for later publication.
        This model depends on the following models: Subject, Session, Staff (for teacher association), Location
        Various default values for this model are determined by values in the settings file.
    """
    DOW_CHOICES = (
        (0, _('Monday')),
        (1, _('Tuesday')),
        (2, _('Wednesday')),
        (3, _('Thursday')),
        (4, _('Friday')),
        (5, _('Saturday')),
        (6, _('Sunday')))
    # id = auto-created
    # students exists as the students signed up for this ClassOffer
    subject = models.ForeignKey('Subject', on_delete=models.SET_NULL, null=True, )
    session = models.ForeignKey('Session', on_delete=models.SET_NULL, null=True, )
    _num_level = models.IntegerField(default=0, editable=False, )
    manager_approved = models.BooleanField(default=settings.ASSUME_CLASS_APPROVE, )
    location = models.ForeignKey('Location', on_delete=models.SET_NULL, null=True, )
    teachers = models.ManyToManyField('Staff', related_name='taught', limit_choices_to={'user__is_active': True}, )
    class_day = models.SmallIntegerField(choices=DOW_CHOICES, default=settings.DEFAULT_KEY_DAY, )
    start_time = models.TimeField()
    skip_weeks = models.PositiveSmallIntegerField(_('skipped mid-session class weeks'), default=0, )
    skip_tagline = models.CharField(max_length=46, blank=True, )
    # resources exits, but only directly connected Resources, not those connected through Subject.
    # # future: class_resources exists, but only includes directly connected Resources, but not those through Subject.

    date_added = models.DateField(auto_now_add=True, )
    date_modified = models.DateField(auto_now=True, )
    objects = ClassOfferManager()

    def model_resources(self, live=False):
        """Include not only self.resources, but also self.subject.resources. """
        # # user = self.request.user
        # # user_val, user_roles = user.user_roles
        # # user_type = 3 if user_val >= 4 else user_val
        # user_type = 3  # TODO: Determine what is wanted for filtering by user role level.
        # try:
        #     result = ClassOffer.objects.filter(id=self.id).get_resources(live=live, type_user=user_type, model=self)
        #     print(result)
        # except Exception as e:
        #     print('Current algorithm raised an error: ')
        #     raise e
        raise NotImplementedError

    @property
    def full_price(self):
        """This is full, at-the-door, price """
        return Decimal(getattr(self.subject, 'full_price', settings.DEFAULT_CLASS_PRICE))

    @property
    def pre_discount(self):
        """Discount given if they sign up and pay in advanced. """
        return Decimal(getattr(self.subject, 'pre_pay_discount', settings.DEFAULT_PRE_DISCOUNT))

    @property
    def multi_discount(self):
        """Does this ClassOffer qualify as one that gets a multiple discount and what discount can it provide? """
        if not self.subject.qualifies_as_multi_class_discount:
            return 0
        else:
            return self.subject.multiple_purchase_discount

    @property
    def pre_price(self):
        """This is the price if they pay in advance. """
        price = self.full_price
        if self.pre_discount > 0:
            price -= self.pre_discount
        return price

    @property
    def skip_week_explain(self):
        """Most of the time there is not a missing week in the middle of session.
            However, sometimes there are holidays that we can not otherwise schedule around.
            This returns some text explaining the skipped week. Generally this is included in class description details.
        """
        explain = "but you still get {} class days".format(self.session.num_weeks)
        # if some skip condition, modify explain with explanation text
        return _(explain)

    @property
    def end_time(self):
        """A time obj (date and timezone unaware) computed based on the start time and subject.num_minutes. """
        start = dt.combine(date(2009, 2, 13), self.start_time)  # arbitrary date on day of timestamp 1234567890.
        end = start + timedelta(minutes=self.subject.num_minutes)
        return end.time()

    @property
    def day(self):
        """Returns a string for the day of the week, plural if there are multiple weeks, for this ClassOffer. """
        day = self.DOW_CHOICES[self.class_day][1]
        day += 's' if self.subject.num_weeks > 1 else ''
        return day

    @property
    def day_short(self):
        day_long = self.day
        ending = "(s)" if day_long.endswith('s') else ""
        return day_long[:3] + ending

    @property
    def num_level(self):
        """When we want a sortable level number. """
        return self._num_level

    def set_num_level(self):
        # TODO: Do we need 'num_level' field, or just going to use value from parent 'Subject'?
        level_dict = Subject.LEVEL_ORDER
        higher = 100 + max(level_dict.values())
        num = level_dict.get(getattr(self.subject, 'level', ''), higher)
        self._num_level = num
        return num

    def save(self, *args, **kwargs):
        self.set_num_level()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('classoffer_detail', args=[str(self.id)])

    def __str__(self):
        return '{} - {}'.format(self.subject, self.session)

    def __repr__(self):
        return '<Class Id: {} | Subject: {} | Session: {} >'.format(self.id, self.subject, self.session)


class AbstractProfile(models.Model):
    """Extending user model to have profile fields as appropriate as either a student or a staff member. """

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True,
                                limit_choices_to={}, )
    bio = models.TextField(max_length=760, blank=True, )  # Staff will override max_length to be bigger.
    date_added = models.DateField(auto_now_add=True, )
    date_modified = models.DateField(auto_now=True, )

    class Meta:
        abstract = True

    @property
    def username(self):
        return self.user.username

    @property
    def full_name(self):
        return self.user.full_name

    def get_full_name(self):
        return self.user.get_full_name()

    def get_absolute_url(self):
        # Usually overwritten by concrete class url name, but this is available as a backup.
        return reverse("profile_user", kwargs={"id": self.user_id})

    def __str__(self):
        return self.full_name

    def __repr__(self):
        return "<Profile: {} | User id: {} >".format(self.full_name, self.user_id)


class Staff(AbstractProfile):
    """A profile model appropriate for Staff users. """

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True,
                                limit_choices_to={'is_staff': True}, )
    listing = models.SmallIntegerField(default=10, blank=True,
                                       help_text=_("Negative numbers will not be shown. "), )
    tax_doc = models.CharField(max_length=9, blank=True, )
    # taught exists from ClassOffer.teachers related_name

    class Meta(AbstractProfile.Meta):
        verbose_name_plural = 'staff'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._meta.get_field('bio').max_length = 1530  # Current for Chris is 1349 characters!

    def get_absolute_url(self):
        return reverse("profile_staff", kwargs={"id": self.user_id})


class Student(AbstractProfile):
    """A profile model appropriate for Student users. """

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True,
                                limit_choices_to={'is_student': True})
    level = models.IntegerField(_('skill level'), default=0, blank=True, )
    taken = models.ManyToManyField(ClassOffer, related_name='students', through='Registration', )
    # interest = models.ManyToManyField(Subject, related_names='interests', through='Requests', )
    credit = models.DecimalField(max_digits=6, decimal_places=2, default=0.0, )
    # TODO: Implement self-referencing key for a 'refer-a-friend' discount.
    # refer = models.ForeignKey(User, symmetrical=False, on_delete=models.SET_NULL,
    #                           null=True, blank=True, related_names='referred', )
    # TODO: The following properties could be extracted further to allow the program admin user
    # to set their own rules for number of versions needed and other version translation decisions.

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self._meta.get_field('user').limit_choices_to = Q(is_student=True)  # {'is_student': True}

    @property
    def highest_subject(self):
        """We will want to know what is the student's class level which by default will be the highest
            class level they have taken. We also want to be able to override this from a teacher or
            admin input to deal with students who have had instruction or progress elsewhere.
        """
        data = self.taken_subjects.aggregate(Max('level_num'))
        max_level = data['level_num__max']
        data['subjects'] = self.taken_subjects.filter(level_num=max_level)
        return data

    @property
    def taken_subjects(self):
        """Since all taken subjects are related through ClassOffer, we check taken to see the subject names. """
        return Subject.objects.filter(id__in=self.taken.values_list('subject', flat=True)).distinct()

    @property
    def beg(self):
        """Completed the two versions of Beginning. """
        # TODO: Allow this mapping logic to be created by admin or in settings.
        ver_map = {'A': ['A', 'C'], 'B': ['B', 'D']}
        goal, data, extra = self.subject_data(level=0, each_ver=1, ver_map=ver_map)
        return extra

    @property
    def l2(self):
        """Completed the four versions of level two. """
        goal, data, extra = self.subject_data(level=1, each_ver=1, exclude='N')
        return extra

    @property
    def l3(self):
        """Completed four versions of level three. """
        goal, data, extra = self.subject_data(level=2, each_ver=1, exclude='N')
        return extra

    def subject_data(self, level=0, each_ver=1, only=None, exclude=('N',), goal_map=None, ver_map=None):
        """
        Used by other properties and methods to determine information on the user's history of subjects.
        Inputs:
            level -> integer:  The row in Subject.LEVEL_CHOICES.
            each_ver -> (integer, None): The default count in the goal. Overwritten by goal_map if present.
            only -> (str, int, list, tuple, None): What VERSION_CHOICES should be included. If None, include all.
            exclude -> (str, int, list, tuple, set, None): What VERSION_CHOICES should be excluded from results.
            The Subject.VERSION_CHOICES may be determined by 'only' and 'exclude':
                int should be an index in VERSION_CHOICES.
                str should match one of first element of each tuple in VERSION_CHOICES.
                for list, tuple, and set: they should be collections of int and/or str that are each valid inputs.
            ver_map -> (dict, None): If the key is a valid 'only' int, it will be converted in a similar way.
                each var_map value -> (list, tuple, dict):
                    As list or tuple, the query will count if VERSION_CHOICES is any of these elements.
                    As a dict, the query is limited to models where model.key=value for all key, value pairs.
            goal_map -> (dict, None): The keys represent VERSION_CHOICES, and values are the goal for each key.
                Each key -> (int, str): Will be handled similarly to 'only' (translating int if possible).
                Each value -> (int): Will be the value in the goal dict for related (modified) key.
            Priority for VERSION_CHOICES is determined in the order: 'ver_map', 'exclude', 'only', and 'goal_map'.
        Outputs:
            goal -> dict: with key -> str of VERSION_CHOICES or label set by ver_map; value -> int for frequency.
            data -> dict: with key -> str identical in goal; value -> int for total found matching parameters.
        Depends on self.taken_subjects (depends on self.taken), ClassOffer.subject, Subject.level, & Subject.version.
        """
        lookup = Subject.VERSION_CHOICES
        goal, agg_dict = {}, {}
        def _clean(key): return lookup[key][0] if isinstance(key, int) and key < len(lookup) else key

        if isinstance(level, int):
            level = Subject.LEVEL_CHOICES[level][0]
        else:
            raise TypeError(_("Expected an int for level parameter. "))
        if only is None:
            pass
        elif isinstance(only, (str, int)):
            only = [only]
        elif not isinstance(only, (list, tuple)):
            raise TypeError(_("For parameter 'only', expected a list, tuple, string, int, or None. "))
        if not exclude:
            exclude = set()
        elif isinstance(exclude, (str, int)):
            exclude = set((exclude,))
        elif isinstance(exclude, (list, tuple)):
            exclude = set(exclude)
        elif not isinstance(exclude, set):
            raise TypeError(_("For parameter 'exclude', expected a list, tuple, string, int, set, or None. "))

        if goal_map:
            if not isinstance(goal_map, dict):
                raise TypeError(_("Expected a dictionary or None for 'goal_map' parameter. "))
            goal = {_clean(k): v for k, v in goal_map.items() if k not in exclude and (not only or k in only)}
        elif only is not None and not ver_map:
            goal = {_clean(key): each_ver for key in only if key not in exclude}
        elif not ver_map:
            goal = {key: each_ver for key, string in lookup if key not in exclude}

        if ver_map:
            if not isinstance(ver_map, dict):
                raise TypeError(_("Expected a dictionary or None for 'goal_map' parameter. "))
            for key, params in ver_map.items():
                key = _clean(key)
                goal[key] = goal.get(key, each_ver)
                q_full = None
                if isinstance(params, (list, tuple)):
                    params = map(_clean, params)
                    q_full = Q(subject__version__in=params, subject__level=level)
                elif isinstance(params, dict):
                    combine_type = params.pop('combine_type', '')
                    if combine_type.upper() == 'OR':
                        raise NotImplementedError("This version of the product does not yet have this feature. ")
                        # TODO: Check if the Q object is correctly making OR statements with the key=value pairs.
                        # q_full = Q()
                        # for key, value in params.items():
                        #     q_full.add(Q(**{key: value}), Q.OR)
                    else:
                        q_full = Q(**params)
                elif params:
                    raise TypeError(_("Expected each 'ver_map' value to be a list, tuple, or dictionary (or falsy). "))
                agg_dict[key] = Count('id', filter=q_full, distinct=True)
        else:  # default data_filters when thee is no ver_map
            agg_dict = {k: Count('id', filter=Q(subject__version=k, subject__level=level), distinct=True) for k in goal}
        # goal is populated. The populated agg_kwargs, level, and self.taken_subjects allow us to make data dictionary
        data = self.taken.aggregate(**agg_dict)
        extra = {'done': False}
        for key in goal:
            extra_value = data.get(key, 0) - goal[key]
            extra[key] = extra_value
            if extra_value < 0:
                return goal, data, extra
        extra['done'] = True
        return goal, data, extra

    def compute_level(self):
        if self.taken.count() < 1:
            return 0
        if self.l3.get('done'):
            return 4 if min(self.l3.values(), default=0) > 0 else 3.5
        if self.l2.get('done'):
            return 3 if min(self.l2.values(), default=0) > 0 else 2.5
        if self.beg.get('done'):
            return 2
        beg_count = self.taken.filter(subject__level=Subject.LEVEL_CHOICES[0][0]).count()
        return 1 if beg_count > 0 else 0

    def get_absolute_url(self):
        return reverse("profile_student", kwargs={"id": self.user_id})

    def save(self, *args, **kwargs):
        if not self.level:
            self.level = self.compute_level()
        super().save(*args, **kwargs)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    profile = None
    if instance.is_student:
        if hasattr(instance, 'student'):
            instance.student.save()
        else:
            profile = Student.objects.create(user=instance)
    if instance.is_staff:
        if hasattr(instance, 'staff'):
            instance.staff.save()
        else:
            profile = Staff.objects.create(user=instance)
    if profile:
        pass
        # print(f"Made a new Profile! {profile} ")
        # instance.profile = profile


class PaymentManager(models.Manager):

    def classRegister(self, register=None, student=None, paid_by=None, **extra_fields):
        """Used for students registering for classoffers, which is the most common usage of our payments """
        print("===== Payment.objects.classRegister (PaymentManager) ======")
        if not isinstance(student, Student):
            raise TypeError('We need a user Student profile passed here.')
        print(student)

        full_price, pre_pay_discount, credit_applied = 0, 0, 0
        description = ''
        multi_discount_list = []
        register = register if isinstance(register, list) else list(register)
        # line_items = []
        for item in register:
            # This could be stored in Registration, or get from ClassOffer
            # purchased = PurchasedItem(name=str(item), sku=str(item), quantity=1,
            #                           price=item.full_price, currency='USD')
            # line_items.append(purchased)
            description = description + str(item) + ', '
            # TODO: DONE? Change to look up the actual class prices & discount
            full_price += item.full_price
            pre_pay_discount += item.pre_discount
            multi_discount_list.append(item.multi_discount)
        # TODO: DONE? Change multiple_discount amount to not be hard-coded.
        multi_discount_list.sort()
        multiple_purchase_discount = multi_discount_list[-2] if len(multi_discount_list) > 1 else 0
        if student.credit > 0:
            credit_applied = student.credit
            # TODO: Remove the used credit from the student profile
            # student.credit_applied = 0
            # student.save()
        full_total = full_price - multiple_purchase_discount - credit_applied
        pre_total = full_total - pre_pay_discount
        # TODO: Insert logic to determine if they owe full_total or pre_total
        paid_by = paid_by if paid_by else student
        user = paid_by.user
        # TODO: If billing address info added to user Student profile, let
        # Payment.objects.classRegister get that info from user profile

        # print("------ Check some pricing processesing ")
        # print(full_price)
        # print(multiple_purchase_discount)
        # print(credit_applied)
        # print('----------')
        # print(full_total)
        # print(pre_pay_discount)
        # print('----------')
        # print(pre_total)
        # print('-=-=-=-=-=-=-=-=-=-=-=-')
        payment_kwargs = dict(
            student=student,
            paid_by=paid_by,
            description=description,
            full_price=full_price,
            pre_pay_discount=pre_pay_discount,
            multiple_purchase_discount=multiple_purchase_discount,
            credit_applied=credit_applied,
            total=Decimal(pre_total),
            tax=Decimal(0),
            billing_first_name=user.first_name,
            billing_last_name=user.last_name,
            billing_country_code=settings.DEFAULT_COUNTRY,
            billing_email=user.email,
            # customer_ip_address='127.0.0.1',
            # TODO: Capture and use _ip_address
            variant='paypal',
            currency='USD',
            # items_list=register,
            )
        payment_kwargs.update(extra_fields)
        payment = self.create(payment_kwargs)
        # TODO; Do we really feel safe passing forward the extra_fields?
        # TODO: Do we need customer_ip_address, and if yes, need to populate now?
        print(payment)
        print("==============----------===========")
        # print(payment.items)
        return payment
    # end class PaymentManager


class Payment(BasePayment):
    """Payment Processing """
    objects = PaymentManager()
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, related_name='payment', )
    paid_by = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, related_name='paid_for', )
    full_price = models.DecimalField(max_digits=6, decimal_places=2, default='0.0', )
    pre_pay_discount = models.DecimalField(max_digits=6, decimal_places=2, default='0.0', )
    multiple_purchase_discount = models.DecimalField(max_digits=6, decimal_places=2, default='0.0', )
    credit_applied = models.DecimalField(max_digits=6, decimal_places=2, default='0.0', )
    billing_country_code = CountryField(_('country'), default=settings.DEFAULT_COUNTRY, max_length=2, blank=True,)
    # items = models.ManyToManyField(ClassOffer, related_name='payments', through='Registration', )

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self._meta.get_field('email').max_length = 191
    #     self._meta.get_field('billing_postcode').max_length = 9
    #     self._meta.get_field('email').max_length = 191
    #     self._meta.get_field('email').max_length = 191

    @property
    def full_total(self):
        """Amount owed if they do not pay before the pre-paid discount deadline """
        return self.full_price - self.multiple_purchase_discount - self.credit_applied

    def pre_total(self):
        """Computed total if they pay before the pre-paid deadline """
        return self.full_total - self.pre_pay_discount

    #   fields needed:
    #   variant = 'paypal', currency = <USD code>, total = ?, description = <string of purchased>
    #   billing_ with: first_name, last_name, address_1, address_2, city, postcode, country_code,
    #   billing_email = models.EmailField(blank=True)

    # # : payment method (PayPal, Stripe, etc)
    # variant = models.CharField(max_length=255)
    # # : Transaction status
    # status = models.CharField(max_length=10, choices=PaymentStatus.CHOICES, default=PaymentStatus.WAITING)
    # fraud_status = models.CharField(_('fraud check'), max_length=10, choices=FraudStatus.CHOICES,
    #                                   default=FraudStatus.UNKNOWN)
    # fraud_message = models.TextField(blank=True, default='')
    # created = models.DateTimeField(auto_now_add=True)
    # modified = models.DateTimeField(auto_now=True)
    # #: Transaction ID (if applicable) from payment processor
    # transaction_id = models.CharField(max_length=255, blank=True)
    # #: Currency code (may be provider-specific)
    # currency = models.CharField(max_length=10)
    # #: Total amount (gross)
    # total = models.DecimalField(max_digits=9, decimal_places=2, default='0.0')
    # delivery = models.DecimalField(max_digits=9, decimal_places=2, default='0.0')
    # tax = models.DecimalField(max_digits=9, decimal_places=2, default='0.0')
    # description = models.TextField(blank=True, default='')
    # billing_first_name = models.CharField(max_length=256, blank=True)
    # billing_last_name = models.CharField(max_length=256, blank=True)
    # billing_address_1 = models.CharField(max_length=256, blank=True)
    # billing_address_2 = models.CharField(max_length=256, blank=True)
    # billing_city = models.CharField(max_length=256, blank=True)
    # billing_postcode = models.CharField(max_length=256, blank=True)
    # billing_country_code = models.CharField(max_length=2, blank=True)
    # billing_country_area = models.CharField(max_length=256, blank=True)
    # billing_email = models.EmailField(blank=True)
    # customer_ip_address = models.GenericIPAddressField(blank=True, null=True)
    # extra_data = models.TextField(blank=True, default='')
    # message = models.TextField(blank=True, default='')
    # token = models.CharField(max_length=36, blank=True, default='')
    # captured_amount = models.DecimalField(max_digits=9, decimal_places=2, default='0.0')

    def get_failure_url(self):
        print('============ Payment.get_failure_url =================')
        return reverse('payment_fail', args=(self.pk,))

    def get_success_url(self):
        print('============ Payment.get_success_url =================')
        return reverse('payment_success', args=(self.pk,))

    def get_done_url(self):
        print('============ Payment.get_success_url =================')
        return reverse('payment_done', args=(self.pk,))

    def get_purchased_items(self):
        # TODO: Write this method.
        # you'll probably want to retrieve these from an associated order
        print('====== Payment.get_purchased_items ===========')
        # registrations = Registration.objects.filter(payment=self.id)
        # items, multi_discount_list, pre_pay_total = [], [], 0
        # for ea in registrations:
        #     selected = ClassOffer.objects.get(id=ea.classoffer)
        #     # TODO: handle determining if pre-pay discount is valid
        #     pre_pay_total += selected.pre_discount
        #     multi_discount_list.append(selected.multi_discount)
        #     item = PurchasedItem(name=str(selected), sku=ea.id, currency='USD',
        #                          price=Decimal(selected.full_price), quantity=1)
        #     items.append(item)
        # if pre_pay_total > 0:
        #     item = PurchasedItem(name='Paid in Advanced Discount', sku='ppd', currency='USD',
        #                          price=Decimal(pre_pay_total), quantity=1)
        #     items.append(item)
        # if len(multi_discount_list) > 1:
        #     multi_discount_list.sort()
        #     discount = multi_discount_list[-2]
        #     item = PurchasedItem(name='Multiple Class Discount', sku='mcd', currency='USD',
        #                          price=Decimal(discount), quantity=1)
        #     items.append(item)
        # for item in items:
        #     yield item
        yield PurchasedItem(name=self.description, sku='HCRF',
                            quantity=1, price=Decimal(self.total), currency='USD')

    @property
    def _payment_description(self):
        result = 'payment '
        if self.paid_by != self.student:
            result += 'by ' + str(self.paid_by)
        result += 'for ' + str(self.student) + ' attending ' + str(self.description)
        return result

    def get_absolute_url(self):
        return reverse('payment', args=[str(self.id)])

    def __str__(self):
        return self._payment_description

    def __repr__(self):
        return "<Payment: {} >".format(self._payment_description)


class Registration(models.Model):
    """This is an intermediary model between a user Student profile and the ClassOffers they are enrolled in.
        Also used to create the class check-in view for the staff.
    """
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, )
    classoffer = models.ForeignKey(ClassOffer, on_delete=models.SET_NULL, null=True, )
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True, )
    paid = models.BooleanField(default=False, )

    @property
    def owed(self):
        """How much is owed by this student currently in this classoffer. """
        if not self.payment:
            return 0
        owed = self.payment.total - self.payment.captured_amount
        if owed > 0:
            owed = self.payment.full_total - self.payment.captured_amount
        return owed

    @property
    def first_name(self):
        return self.student.user.first_name

    @property
    def last_name(self):
        return self.student.user.last_name

    @property
    def _get_full_name(self):
        return getattr(self.student, '_get_full_name', None) or _("Name Not Found")

    @property
    def credit(self):
        return self.student.credit

    # TODO: If the following (or above) properties are not used, remove them.

    @property
    def reg_class(self):
        return self.classoffer.subject.level
    # reg_class.admin_order_field = 'classoffer__subject__level'

    @property
    def session(self):
        return self.classoffer.session
    # reg_session.admin_order_field = 'classoffer__session__key_day_date'

    @property
    def class_day(self):
        return self.classoffer.class_day

    @property
    def start_time(self):
        return self.classoffer.start_time

    @property
    def _pay_report(self):
        return 'Paid' if self.paid else str(self.owed)

    def __str__(self):
        return f"{self._get_full_name} - {self.classoffer} - {self._pay_report}"

    def __repr__(self):
        values = (self.classoffer, self._get_full_name, self._pay_report)
        return "<Registration: {} | User: {} | Owed: {} >".format(*values)


def resource_filepath(instance, filename):
    # file will be uploaded to one of these formats:
    # MEDIA_ROOT/subject/level/avail/type/all_version_name
    # MEDIA_ROOT/subject/level/avail/type/classoffer_version_name
    # MEDIA_ROOT/other/type/name
    path = ''
    model_type = instance.related_type
    ct = instance.content_type
    obj = None
    if model_type == 'Subject':
        sess = 'all'
        obj = instance.subject
    elif model_type == 'ClassOffer':
        sess = str(instance.classoffer.session.name).lower()
        obj = instance.classoffer.subject
    else:
        path += f'/other/{ct}/{filename}'
        return path
    level = str(obj.level).lower()
    version = str(obj.version).lower()
    avail = str(instance.avail)
    path += f'subject/{level}/{avail}/{ct}/{sess}_{version}_{filename}'
    return path


class Notify(EmailMessage):
    """Usually used for sending emails, or other communcation methods, to users. """

    @classmethod
    def register(cls, selected=None, student=None, paid_by=None, **kwargs):
        """This is for when a user is registered for a ClassOffer. """
        from django.core.mail import send_mail
        from pprint import pprint

        print("========== Notify.register ==============")
        if not student and not paid_by:
            # TODO: raise error or other catch
            return False
        user = paid_by.user if paid_by else student.user
        to_email = getattr(user, 'email', None)
        if not to_email:
            # TODO: raise error or other catch
            return False
        from_email = settings.DEFAULT_FROM_EMAIL
        subject = "Your Class Registration"
        class_list = [str(ea) for ea in selected]
        purchase_list = ', '.join(class_list)
        body = f"You signed up {student} to attend {purchase_list}"
        pprint({
            "***send_email***": "============================",
            "subject": subject,
            "body": body,
            "from_email": from_email,
            "to_email": to_email
        })
        mail_sent = 0
        try:
            mail_sent = send_mail(subject, body, from_email, [to_email])
        except Exception as e:
            print("Send Mail Error", e)
        # instantiate a new Notify to send an email
        print(f"Mail Sent: {mail_sent}")
        return mail_sent


# end models.py

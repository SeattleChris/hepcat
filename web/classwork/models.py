from django.db import models
from django.db.models import Q, Count, Max  # , F, Min, Avg, Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
# from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.conf import settings
from django.urls import reverse
from decimal import Decimal  # used for Payments
from payments import PurchasedItem
from payments.models import BasePayment
from datetime import date, timedelta, datetime as dt
# from django.contrib.auth import get_user_model
# User = get_user_model()
# TODO: Should we be using get_user_model() instead of settings.AUTH_USER_MODEL ?

# Create your models here.
# TODO: Implement calling resource_filepath for resource uploads.

# TODO: Use ForeignKey.limit_choices_to where appropriate.
# TODO: Update to appropriately use ForeignKey.related_name
# TODO: Decide if any ForeignKey should actually be ManytoManyField (incl above)
# TODO: Add a field for "draft" vs. ready to publish for ClassOffer, Subject, Session?
# TODO: Add @staff_member_required decorator to admin views?


class SiteContent(models.Model):
    """ Public content for different sections of the site. """
    # id = auto-created
    name = models.CharField(max_length=120, help_text=_('Descriptive name used to find this content'))
    text = models.TextField(blank=True, help_text=_('Text chunk used in page or email publication'))

    date_added = models.DateField(auto_now_add=True, )
    date_modified = models.DateField(auto_now=True, )

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<SiteContent: {} >'.format(self.name)


class Location(models.Model):
    """ This stores information about each location where ClassOffers may be held. """
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

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Location: {} | Link: {} >'.format(self.name, self.map_link)


class Resource(models.Model):
    """ Subjects and ClassOffers can have various resources released to the students at
        different times while attending a ClassOffer or after they have completed the session.
        Subjects and ClassOffers can have various resources available to the instructors
        to aid them in class preperation and presentation.
    """
    # TODO: Make validation checks on new Resource instances
    # TODO: does it require an admin/teacher response before released?
    # TODO: Add sending email feature.

    MODEL_CHOICES = (
        ('Subject', _('Subject')),
        ('ClassOffer', _('ClassOffer')),
        ('Other', _('Other')))
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
        (0, _('On Sign-up, before week 1)')),
        (1, _('After week 1')),
        (2, _('After week 2')),
        (3, _('After week 3')),
        (4, _('After week 4')),
        (5, _('After week 5')),
        # TODO: Make this adaptable to any class duration.
        # TODO: Make options for weekly vs. daily classes?
        (200, _('After completion')))

    # id = auto-created
    related_type = models.CharField(max_length=15, default='Subject', choices=MODEL_CHOICES, editable=False, )
    subject = models.ForeignKey('Subject', on_delete=models.SET_NULL, null=True, blank=True, )
    classoffer = models.ForeignKey('ClassOffer', on_delete=models.SET_NULL, null=True, blank=True, )
    content_type = models.CharField(max_length=15, choices=CONTENT_CHOICES, )
    user_type = models.PositiveSmallIntegerField(default=1, choices=USER_CHOICES, help_text=_('Who is this for?'), )
    avail = models.PositiveSmallIntegerField(default=0, choices=PUBLISH_CHOICES,
                                             help_text=_('When is this resource available?'), )
    expire = models.PositiveSmallIntegerField(default=0, help_text=_('Number of published weeks? (0 for always)'), )
    imagepath = models.ImageField(upload_to='resource/', help_text=_('If an image, upload here'), blank=True, )
    filepath = models.FileField(upload_to='resource/', help_text=_('If a file, upload here'), blank=True, )
    link = models.URLField(max_length=191, help_text=_('External or Internal links go here'), blank=True, )
    text = models.TextField(help_text=_('Text chunk used in page or email publication'), blank=True, )
    title = models.CharField(max_length=60, )
    description = models.TextField(blank=True, )

    date_added = models.DateField(auto_now_add=True, )
    date_modified = models.DateField(auto_now=True, )

    def publish(self, classoffer):
        """ Bool if this resource is available for users who attended a given classoffer. """
        pub_delay = 3
        week = self.avail if self.avail != 200 else classoffer.subject.num_weeks
        delay = pub_delay+7*week
        now = date.today()
        start = classoffer.start_date
        avail_date = min(now, start) if week == 0 else start + timedelta(days=delay)
        expire_date = None if self.expire == 0 else avail_date + timedelta(weeks=self.expire)
        if expire_date and now > expire_date:
            return False
        return now >= avail_date

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

    def save(self, *args, **kwargs):
        if self.subject: self.related_type = 'Subject'  # noqa e701
        elif self.classoffer: self.related_type = 'ClassOffer'  # noqa e701
        else: self.related_type = 'Other'  # noqa e701
        super().save(*args, **kwargs)

    def __str__(self):
        return "{} - {} - {}".format(self.title, self.related_type, self.content_type)

    def __repr__(self):
        return '<Resource: {} | Type: {} >'.format(self.related_type, self.content_type)


class Subject(models.Model):
    """ A 'Subject' is the general information and teaching content intended to be covered. The details of what was
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
    title = models.CharField(max_length=125, default=_('Untitled'), )
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

    date_added = models.DateField(auto_now_add=True, )
    date_modified = models.DateField(auto_now=True, )

    def compute_level_num(self, level_value=None, set_self=True):
        """ Translate and assign the number associated to the value in 'level' field, assigning 0 if not determined. """
        level_value = level_value if level_value is not None else self.level
        num = self.LEVEL_ORDER.get(level_value, 0)
        if set_self:
            self.level_num = num
        return num

    @property
    def _str_slug(self):
        slug = f'{self.level}{self.version}'
        if self.level not in ['Beg', 'L2']:
            slug += f': {self.title}'
        return slug

    def save(self, *args, **kwargs):
        if not self.level_num:
            self.compute_level_num()
        super().save(*args, **kwargs)

    def __str__(self):
        return self._str_slug

    def __repr__(self):
        return '<Subject: {} | Level: {} | Version: {} >'.format(self.title, self.level, self.version)


# class LevelGroup(models.Model):
#     """ Sometimes there will be multiple Subjects (classes)
#         that, as a group, are meant to be taken before
#         a student has completed that Subject.
#     """
#     # id = auto-created
#     title = models.CharField(max_length=8, choices=Subject.LEVEL_CHOICES, default='Spec')
#     # collection = models.ManyToManyField('Subject', symmetrical=True)
#     collection = models.ForeignKey('Subject', on_delete=models.CASCADE)


def default_publish(): return Session._default_date('publish_date')


def default_key_day(): return Session._default_date('key_day_date')


class Session(models.Model):
    """ Classes are offered and published according to which session they belong.
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
        """ Return the date for whichever is the actual first class day. """
        first_date = self.key_day_date
        if self.max_day_shift < 0:
            first_date += timedelta(days=self.max_day_shift)
        return first_date

    @property
    def end_date(self):
        """ Return the date for the last class day. """
        last_date = self.key_day_date + timedelta(days=7*(self.num_weeks + self.skip_weeks - 1))
        if (self.max_day_shift < 0 and self.flip_last_day) or \
           (self.max_day_shift > 0 and not self.flip_last_day):
            # A) Early non-key day has skipped to end; B) Non-key day came after, and skipped weeks hasn't changed that.
            last_date += timedelta(days=self.max_day_shift)
        return last_date

    @property
    def prev_session(self):
        """ Return the Session that comes before the current Session, or 'None' if none exists. """
        return self.last_session(since=self.key_day_date)

    @property
    def next_session(self):
        """ Returns the Session that comes after the current Session, or 'None' if none exists. """
        key_day = self.key_day_date
        key_day = key_day() if callable(key_day) else key_day
        key_day = key_day.isoformat() if isinstance(key_day, (date, dt)) else key_day
        later = Session.objects.filter(key_day_date__gt=key_day)
        next_one_or_none = later.order_by('key_day_date').first()
        return next_one_or_none

    @classmethod
    def last_session(cls, since=None):
        """ Returns the Session starting the latest, or latest prior to given 'since' date. Return None if none. """
        query = cls.objects
        # TODO: Look into get_next_by_FOO() and get_previous_by_FOO(), they raise Model.DoesNotExist
        if since:
            # TODO: Check isinstance an appropriate datetime obj
            query = query.filter(key_day_date__lt=since)
        return query.order_by('-key_day_date').first()

    @classmethod
    def _default_date(cls, field, since=None):
        """ Compute a default value for 'key_day_date' or 'publish_date' field. """
        allowed_fields = ('key_day_date', 'publish_date')
        if field not in allowed_fields:
            raise ValueError(_("Not a valid field parameter: {} ".format(field)))
        now = date.today()
        final_session = cls.last_session(since=since)
        while final_session is not None and final_session.num_weeks < settings.SESSION_MINIMUM_WEEKS:
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
        """ Assumes unaffected by skipped weeks. Based on parameters from settings. """
        minimum_session_weeks = settings.SESSION_MINIMUM_WEEKS
        default_expire = settings.DEFAULT_SESSION_EXPIRE
        short_expire = settings.SHORT_SESSION_EXPIRE
        if not key_day:
            key_day = self.key_day_date
        adj = self.max_day_shift if self.max_day_shift > 0 else 0
        adj += default_expire if self.num_weeks > minimum_session_weeks else short_expire
        expire = key_day + timedelta(days=adj)
        return expire

    def clean(self):
        """ Modifies values for validity checks and if needed to avoid overlapping published Sessions.
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
        """ If given an 'update_fields' list of field names, directly saves if doing so won't break expire_date.
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

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Session: {} >'.format(self.name)


class ClassOffer(models.Model):
    """ Different classes can be offered at different times and scheduled for later publication.
        This model depends on the following models: Subject, Session, Profile (for teacher association), Location
        Various default values for this model are determined by values in the settings file.
    """
    DOW_CHOICES = (
        (0, _('Monday')),
        (1, _('Tuesday')),
        (2, _('Wednesday')),
        (3, _('Thursday')),
        (4, _('Friday')),
        (5, _('Saturday')),
        (6, _('Sunday'))
    )
    # id = auto-created
    # self.students exists as the students signed up for this ClassOffer
    subject = models.ForeignKey('Subject', on_delete=models.SET_NULL, null=True, )
    session = models.ForeignKey('Session', on_delete=models.SET_NULL, null=True, )
    _num_level = models.IntegerField(default=0, editable=False, )
    manager_approved = models.BooleanField(default=settings.ASSUME_CLASS_APPROVE, )
    location = models.ForeignKey('Location', on_delete=models.SET_NULL, null=True, )
    # TODO: later on teachers will selected from users - teachers.
    teachers = models.CharField(max_length=125, default='Chris Chapman', )
    class_day = models.SmallIntegerField(choices=DOW_CHOICES, default=settings.DEFAULT_KEY_DAY, )
    start_time = models.TimeField()
    skip_weeks = models.PositiveSmallIntegerField(_('skipped mid-session class weeks'), default=0, )
    skip_tagline = models.CharField(max_length=46, blank=True, )

    date_added = models.DateField(auto_now_add=True, )
    date_modified = models.DateField(auto_now=True, )

    @property
    def full_price(self):
        """ This is full, at-the-door, price """
        return Decimal(getattr(self.subject, 'full_price', settings.DEFAULT_CLASS_PRICE))

    @property
    def pre_discount(self):
        """ Discount given if they sign up and pay in advanced. """
        return Decimal(getattr(self.subject, 'pre_pay_discount', settings.DEFAULT_PRE_DISCOUNT))

    @property
    def multi_discount(self):
        """ Does this ClassOffer qualify as one that gets a multiple discount and what discount can it provide? """
        if not self.subject.qualifies_as_multi_class_discount:
            return 0
        else:
            return self.subject.multiple_purchase_discount

    @property
    def pre_price(self):
        """ This is the price if they pay in advance. """
        price = self.full_price
        if self.pre_discount > 0:
            price -= self.pre_discount
        return price

    @property
    def skip_week_explain(self):
        """ Most of the time there is not a missing week in the middle of session.
            However, sometimes there are holidays that we can not otherwise schedule around.
            This returns some text explaining the skipped week. Generally this is included in class description details.
        """
        explain = "but you still get {} class days".format(self.session.num_weeks)
        # if some skip condition, modify explain with explanation text
        return _(explain)

    @property
    def end_time(self):
        """ A time obj (date and timezone unaware) computed based on the start time and subject.num_minutes. """
        start = dt.combine(date(2009, 2, 13), self.start_time)  # arbitrary date on day of timestamp 1234567890.
        end = start + timedelta(minutes=self.subject.num_minutes)
        return end.time()

    @property
    def day(self):
        """ Returns a string for the day of the week, plural if there are multiple weeks, for this ClassOffer. """
        day = self.DOW_CHOICES[self.class_day][1]
        day += 's' if self.subject.num_weeks > 1 else ''
        return day

    @property
    def start_date(self):
        """ Returns a date object (time and timezone unaware) for the first day of this ClassOffer. """
        start = self.session.key_day_date
        dif = self.class_day - start.weekday()
        if dif == 0:
            return start
        shift = self.session.max_day_shift
        if dif < shift < 0 or 0 < dif + 7 < shift:
            dif += 7
        elif shift < dif - 7 < 0 or 0 < shift < dif:
            dif -= 7
        return start + timedelta(days=dif)

    @property
    def end_date(self):
        """ Returns the computed end date (time and timezone unaware) for this class offer. """
        return self.start_date + timedelta(days=7*(self.subject.num_weeks + self.skip_weeks - 1))

    @property
    def day_short(self):
        day_long = self.day
        ending = "(s)" if day_long.endswith('s') else ""
        return day_long[:3] + ending

    @property
    def num_level(self):
        """ When we want a sortable level number. """
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

    def __str__(self):
        return '{} - {}'.format(self.subject, self.session)

    def __repr__(self):
        return '<Class Id: {} | Subject: {} | Session: {} >'.format(self.id, self.subject, self.session)


class Profile(models.Model):
    """ Extending user model to have profile fields as appropriate as either a student or a staff member. """
    # TODO: Allow users to modify their profile.
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True, )
    bio = models.TextField(max_length=1530, blank=True, )  # Current for Chris is 1349 characters!
    level = models.IntegerField(_('skill level'), default=0, blank=True, )
    taken = models.ManyToManyField(ClassOffer, related_name='students', through='Registration', )
    # interest = models.ManyToManyField(Subject, related_names='interests', through='Requests', )
    credit = models.FloatField(_('class payment credit'), default=0, )
    # TODO: Implement self-referencing key for a 'refer-a-friend' discount.
    # refer = models.ForeignKey(User, symmetrical=False, on_delete=models.SET_NULL,
    #                           null=True, blank=True, related_names='referred', )

    date_added = models.DateField(auto_now_add=True, )
    date_modified = models.DateField(auto_now=True, )
    # TODO: The following properties could be extracted further to allow the program admin user
    # to set their own rules for number of versions needed and other version translation decisions.

    @property
    def highest_subject(self, subjects=True):  # , classoffers=False
        """ We will want to know what is the student's class level which by default will be the highest
            class level they have taken. We also want to be able to override this from a teacher or
            admin input to deal with students who have had instruction or progress elsewhere.
        """
        data = self.taken_subjects.aggregate(Max('level_num'))
        max_level = data['level_num__max']
        if subjects:
            data['subjects'] = self.taken_subjects.filter(level_num=max_level)
        # if classoffers:
        #     data['classoffers'] = self.taken.filter(subject__level_num=max_level).order_by('-session_id__key_day_date')
        #     # TODO: Determine if ClassOffer should have this value or if we should get it from Subject.
        #     by_classoffer = self.taken.aggregate(max_classoffer=Max('_num_level'))
        #     c_max = by_classoffer['max_classoffer']
        #     by_classoffer['collect_classoffer'] = self.taken.filter(_num_level=c_max).order_by('-session__key_day_date')
        #     data.update(by_classoffer)
        return data

    @property
    def taken_subjects(self):
        """ Since all taken subjects are related through ClassOffer, we check taken to see the subject names. """
        return Subject.objects.filter(id__in=self.taken.values_list('subject')).distinct()

    @property
    def beg(self):
        """ Completed the two versions of Beginning. """
        ver_map = {'A': ['A', 'C'], 'B': ['B', 'D']}
        goal, data, extra = self.subject_data(level=0, each_ver=1, ver_map=ver_map)
        return extra

    @property
    def l2(self):
        """ Completed the four versions of level two. """
        goal, data, extra = self.subject_data(level=1, each_ver=1, exclude='N')
        return extra

    @property
    def l3(self):
        """ Completed four versions of level three. """
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
                if isinstance(params, (list, tuple)):
                    params = map(_clean, params)
                    q_full = Q(subject__version__in=params, subject__level=level)
                elif isinstance(params, dict):
                    combine_type = params.pop('combine_type', '')
                    if combine_type.upper() == 'OR':
                        # TODO: Check if the Q object is correctly making OR statements with the key=value pairs.
                        q_full = Q()
                        for key, value in params.items():
                            q_full.add(Q(**{key: value}), Q.OR)
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

    @property
    def username(self):
        return self.user.username

    @property
    def full_name(self):
        return self.user.full_name

    def get_full_name(self):
        return self.user.get_full_name()

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

    def save(self, *args, **kwargs):
        if not self.level:
            self.level = self.compute_level()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name

    def __repr__(self):
        return "<Profile: {} | User id: {} >".format(self.full_name, self.user.id)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


class PaymentManager(models.Manager):

    def classRegister(self, register=None, student=None, paid_by=None, **extra_fields):
        """ Used for students registering for classoffers, which is the most common usage of our payments """
        print("===== Payment.objects.classRegister (PaymentManager) ======")
        if not isinstance(student, Profile):
            raise TypeError('We need a user Profile passed here.')
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
        # TODO: If billing address info added to user Profile, let
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
        payment = self.create(
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
            billing_country_code='US',
            billing_email=user.email,
            # customer_ip_address='127.0.0.1',
            # TODO: Capture and use _ip_address
            variant='paypal',
            currency='USD',
            # items_list=register,
            **extra_fields
            )
        # TODO; Do we really feel safe passing forward the extra_fields?
        # TODO: Do we need customer_ip_address, and if yes, need to populate now?
        print(payment)
        print("==============----------===========")
        # print(payment.items)
        return payment
    # end class PaymentManager


class Payment(BasePayment):
    """ Payment Processing """
    objects = PaymentManager()
    student = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, related_name='payment', )
    paid_by = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, related_name='paid_for', )
    full_price = models.DecimalField(max_digits=6, decimal_places=2, default='0.0', )
    pre_pay_discount = models.DecimalField(max_digits=6, decimal_places=2, default='0.0', )
    multiple_purchase_discount = models.DecimalField(max_digits=6, decimal_places=2, default='0.0', )
    credit_applied = models.DecimalField(max_digits=6, decimal_places=2, default='0.0', )
    # items = models.ManyToManyField(ClassOffer, related_name='payments', through='Registration', )

    @property
    def full_total(self):
        """ Amount owed if they do not pay before the pre-paid discount deadline """
        return self.full_price - self.multiple_purchase_discount - self.credit_applied

    def pre_total(self):
        """ Computed total if they pay before the pre-paid deadline """
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
    # def get_form(self):
    #     pass

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

    def __str__(self):
        return self._payment_description

    def __repr__(self):
        return "<Payment: {} >".format(self._payment_description)


class Registration(models.Model):
    """ This is an intermediary model between a user Profile and the ClassOffers they are enrolled in.
        Also used to create the class check-in view for the staff.
    """
    student = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, )
    classoffer = models.ForeignKey(ClassOffer, on_delete=models.SET_NULL, null=True, )
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True, )
    paid = models.BooleanField(default=False, )

    @property
    def owed(self):
        """ How much is owed by this student currently in this classoffer. """
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
    # class Meta:
    #     order_with_respect_to = 'classoffer'
    #     pass

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
    """ Usually used for sending emails, or other communcation methods, to users. """

    @classmethod
    def register(cls, selected=None, student=None, paid_by=None, **kwargs):
        """ This is for when a user is registered for a ClassOffer. """
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

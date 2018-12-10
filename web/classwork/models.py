# from __future__ import unicode_literals

# from django.contrib.auth.models import User
from django.db import models
# from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
# from django.utils.translation import ugettext_lazy as _
from datetime import datetime, timedelta
# Create your models here.

# TODO: Use ForeignKey.limit_choices_to where appropriate.
# TODO: Update to appropriatly use ForiegnKey.related_name
# TODO: Decide if any ForiegnKey should actually be ManytoManyField (incl above)
# TODO: Add a field for "draft" vs. ready to publish for ClassOffer, Subject, Session?
# TODO: Add @staff_member_required decorator to admin views?

# class MyUserManager(BaseUserManager):
#     """ Custom user manager to allow emails as default unique identifiers for auth.
#         We will need a backup for email to allow a user to sign-up a "friend".
#         We also may need a backup username when a student does not want to give
#         an email address, but still joins and pays for a class or service.
#     """

#     def normalize_email(self):
#         """ We want to lowercase the user part of the email.
#             By default (super) lowercases the domain name.
#         """
#         email = super().normalize_email()  # In case in the future it does more
#         try:
#             email_name, domain_part = email.strip().rsplit('@', 1)
#         except ValueError:
#             pass
#         else:
#             email = email_name.casefold() + '@' + domain_part.lower()
#         return email

#     def _create_user(self, email, password, **extra_fields):
#         """ Creates and saves a User with the given email and password.
#         """
#         all_users = []
#         username = ''
#         uses_alt_username = False

#         # populate all_users with the usernames in the db
#         # if email not in all_usernames:
#         if not email or self.email is None or self.email in all_users:
#             username = self.first_name + '_' + self.last_name
#             # normalize username, or first_name and last_name before username created
#             uses_alt_username = True

#         else:
#             username = self.normalize_username(self.email)
#         username = self.normalize_username(username)

#         email = self.normalize_email(email)
#         user = self.model(email=email, **extra_fields)
#         user.set_password(password)
#         user.save()
#         return user

#     def create_superuser(self, email, password, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#         extra_fields.setdefault('is_active', True)

#         if extra_fields.get('is_staff') is not True:
#             raise ValueError('Superuser must have is_staff=True.')
#         if extra_fields.get('is_superuser') is not True:
#             raise ValueError('Superuser must have is_superuser=True.')
#         return self._create_user(email, password, **extra_fields)


# class MyUser(AbstractBaseUser, PermissionsMixin):
#     """ We modify the default user to allow the email to be the default username.

#     """
#     is_staff = models.BooleanField(
#         _('staff status'),
#         default=False,
#         help_text=_('Designates whether the user can login to admin.'),
#     )
#     is_active = models.BooleanField(
#         _('active'),
#         default=True,
#         help_text=_(
#             'Designates whether this user should be treated as active. '
#             'Unselect this instead of deleting accounts.'
#         ),
#     )
#     first_name = models.CharField(max_length=125)
#     last_name = models.CharField(max_length=125)
#     email = models.EmailField(max_length=255, unique=False, blank=True)
#     username = models.CharField(max_length=255, blank=True, unique=True)
#     uses_alt_username = models.BooleanField(default=False)
#     objects = MyUserManager()
#     USERNAME_FIELD = 'username'
#     REQUIRED_FIELDS = ['first_name', 'last_name']

#     def set_username(self, parameter_list):
#         """ Check to see if this email is already used as a username
#             If available, set the username to the email value
#             If not available, user 'first_name' + '_' + 'last_name'
#         """
#         pass

#     def __str__(self):
#         return self.email

#     def get_full_name(self):
#         return self.email

#     def get_short_name(self):
#         return self.email


class Subject(models.Model):
    """ We are calling the general information for a potential dance class
        offering a "Subject". For a give Subject, there may be different
        instances of when it is offered, which will be in the Classes model.
    """
    # id = auto-created
    LEVEL_CHOICES = (
        ('Beg', 'Beginning'),
        ('L2', 'Lindy 2'),
        ('L3', 'Lindy 3'),
        ('Spec', 'Special Focus'),
        ('WS', 'Workshop'),
        ('Priv', 'Private Lesson'),
        ('PrivSet', 'Private - Multiple Lessons'),
        ('Other', 'Other')
    )
    VERSION_CHOICES = (
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('N', 'NA'),
    )
    level = models.CharField(max_length=8, choices=LEVEL_CHOICES, default='Spec')
    version = models.CharField(max_length=1, choices=VERSION_CHOICES)
    title = models.CharField(max_length=125, default='Untitled')
    short_desc = models.CharField(max_length=100)
    num_weeks = models.PositiveSmallIntegerField(default=5)
    num_minutes = models.PositiveSmallIntegerField(default=60)
    description = models.TextField()
    syllabus = models.TextField(blank=True)
    teacher_plan = models.TextField(blank=True)
    video_wk1 = models.URLField(blank=True)
    video_wk2 = models.URLField(blank=True)
    video_wk3 = models.URLField(blank=True)
    video_wk4 = models.URLField(blank=True)
    video_wk5 = models.URLField(blank=True)
    email_wk1 = models.TextField(blank=True)
    email_wk2 = models.TextField(blank=True)
    email_wk3 = models.TextField(blank=True)
    email_wk4 = models.TextField(blank=True)
    email_wk5 = models.TextField(blank=True)
    image = models.URLField(blank=True)
    # image = models.ImageField(upload_to=MEDIA_ROOT)

    # created_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='subjects')
    date_added = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)

    def __str__(self):
        slug = f'{self.level}{self.version}'
        if self.level not in ['Beg', 'L2']:
            slug += f': {self.title}'
        return slug

    def __repr__(self):
        return f'<Subject: {self.title} | Level: {self.level} | Version: {self.version} >'


class Session(models.Model):
    """ Classes are offered and published according to which session they belong.
        Each session starts on a given date of the key day of the week.
    """
    # id = auto-created
    name = models.CharField(max_length=15)
    key_day_date = models.DateField(verbose_name='Main Class Start Date')
    max_day_shift = models.SmallIntegerField(verbose_name='Number of days other classes are away from Main Class')
    num_weeks = models.PositiveSmallIntegerField(default=5)
    # TODO: Later on we will do some logic to auto-populate the publish and expire dates
    publish_date = models.DateField(blank=True)
    expire_date = models.DateField(blank=True)
    # TODO: Make sure class session publish times can NOT overlap

    def start_date(self):
        """ What is the actual first class day for the session?
        """
        first_date = self.key_day_date
        if self.max_day_shift < 0:
            first_date += timedelta(days=self.max_day_shift)
        return first_date

    def end_date(self):
        """ What is the actual last class day for the session?
        """
        last_date = self.key_day_date + timedelta(days=7*self.num_weeks)
        if self.max_day_shift > 0:
            last_date += timedelta(days=self.max_day_shift)
        return last_date

    def prev_expire_date(self):
        """ Query for the Session in DB that comes before the current Session.
            Return this previous Session expire_date.
        """
        pass

    # created_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='subjects')
    date_added = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)

    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return f'{self.name}'


class ClassOffer(models.Model):
    """ Different classes can be offered at different times and scheduled
        for later publication. Will pull from the following models:
            Subject, Session, Teachers, Location
    """
    # id = auto-created
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE)
    session = models.ForeignKey('Session', on_delete=models.CASCADE)
    # TODO: later on location will be selected from Location model
    # location = models.ForeignKey('Location', on_delete=models.CASCADE)
    # TODO: later on teachers will selected from users - teachers.
    teachers = models.CharField(max_length=125, default='Chris Chapman')
    DOW_CHOICES = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday')
    )
    class_day = models.SmallIntegerField(choices=DOW_CHOICES, default=3)
    start_time = models.TimeField()

    def end_time(self):
        """ For a given subject, the time duration is set. So now this
            ClassOffer instance has set the start time, end time is knowable.
        """
        # TODO: compute and return the end time of the class offer
        # return self.start_time + timedelta(minutes=self.subject.num_minutes)
        t = self.start_time
        # t += 60 * self.subject.num_minutes
        return t

    def start_date(self):
        """ Depends on class_day, Session dates, and possibly on
            Session.max_day_shift being positive or negative.
        """
        start = self.session.key_day_date
        dif = self.class_day - start.weekday()
        if dif == 0:
            return start
        shift, complement, move = self.session.max_day_shift, 0, 0

        if dif < 0: complement = dif + 7
        if dif > 0: complement = dif - 7
        if shift < 0:
            move = min(dif, complement)
            if move < shift:
                move = max(dif, complement)
        if shift > 0:
            move = max(dif, complement)
            if move > shift:
                move = min(dif, complement)
        start += timedelta(days=move)
        return start

    def end_date(self):
        """ Returns the computed end date for this class offer
        """
        return self.start_date() + timedelta(days=7*self.subject.num_weeks)

    # slug = models.SlugField(editable=False, default=get_slug())
    # created_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='classoffers')
    date_added = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)

    def __str__(self):
        return f'{self.subject} - {self.session}'

    def __repr__(self):
        return f'<Class Id: {self.id} | Subject: {self.subject} | Session: {self.session}>'


class Location(models.Model):
    """ ClassOffers may be at various locations.
        This stores information about each location.
    """
    # id = auto-created
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=120)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=120, default='Seattle')
    state = models.CharField(max_length=63, default='WA')
    zipcode = models.CharField(max_length=15)
    map_google = models.URLField(verbose_name="Google Maps Link")

    # created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='locations')
    date_added = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)

    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return f'<Location: {self.name} | Link: {self.map_google} >'


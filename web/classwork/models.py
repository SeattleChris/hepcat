# from __future__ import unicode_literals
from django.db import models
# from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
# from django.utils.translation import ugettext_lazy as _
from datetime import datetime, timedelta
# from django.contrib.auth.models import User
# from django.contrib.auth import get_user_model
# User = get_user_model()
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal  # used for Payments model
from payments import PurchasedItem
from payments.models import BasePayment


# Create your models here.

# TODO: Use ForeignKey.limit_choices_to where appropriate.
# TODO: Update to appropriatly use ForiegnKey.related_name
# TODO: Decide if any ForiegnKey should actually be ManytoManyField (incl above)
# TODO: Add a field for "draft" vs. ready to publish for ClassOffer, Subject, Session?
# TODO: Add @staff_member_required decorator to admin views?


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


class Subject(models.Model):
    """ We are calling the general information for a potential dance class
        offering a "Subject". For a give Subject, there may be different
        instances of when it is offered, which will be in the Classes model.
    """
    # id = auto-created

    LEVEL_CHOICES = (
        ('Beg', 'Beginning'),
        ('L2', 'Lindy 2'),
        # Elsewhere our code expects the first 2 elements to be however we
        # represent our Beginning and Level 2 class series
        ('L3', 'Lindy 3'),
        ('Spec', 'Special Focus'),
        ('WS', 'Workshop'),
        ('Priv', 'Private Lesson'),
        ('PrivSet', 'Private - Multiple Lessons'),
        ('Other', 'Other')
    )
    LEVEL_ORDER = {
        'Beg': 1,
        'L2': 2,
        'L3': 3,
        'Spec': 3,
        'L4': 4,
    }
    VERSION_CHOICES = (
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('N', 'NA'),
    )
    level = models.CharField(max_length=8, choices=LEVEL_CHOICES, default='Spec')
    # level_group = models.ManyToManyField('self')
    # num_level = models.IntegerField(default=0, editable=False)
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

    date_added = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)

    def __str__(self):
        slug = f'{self.level}{self.version}'
        if self.level not in ['Beg', 'L2']:
            slug += f': {self.title}'
        return slug

    def __repr__(self):
        return f'<Subject: {self.title} | Level: {self.level} | Version: {self.version} >'

    def num_level(self):
        """ When we want a sortable level number
        """
        level_dict = self.LEVEL_ORDER
        num = level_dict[self.level] if self.level in level_dict else 0
        return num

    # def save(self, *args, **kwargs):
    #     self.num_level = self.set_num_level()
    #     super().save(*args, **kwargs)


# class LevelGroup(models.Model):
#     """ Sometimes there will be multiple Subjects (classes)
#         that, as a group, are meant to be taken before
#         a student has completed that Subject.
#     """
#     # id = auto-created
#     title = models.CharField(max_length=8, choices=Subject.LEVEL_CHOICES, default='Spec')
#     # collection = models.ManyToManyField('Subject', symmetrical=True)
#     collection = models.ForeignKey('Subject', on_delete=models.CASCADE)


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
    # self.students exists as the students signed up for this ClassOffer
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE)
    session = models.ForeignKey('Session', on_delete=models.CASCADE)
    num_level = models.IntegerField(default=0, editable=False)
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

    date_added = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)

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

    def set_num_level(self):
        """ When we want a sortable level number
        """
        level_dict = Subject.LEVEL_ORDER
        higher = 100 + max(level_dict.values)
        num = 0
        try:
            num = level_dict[self.subject.level]
        except KeyError:
            num = higher
        return num

    def __str__(self):
        return f'{self.subject} - {self.session}'

    def __repr__(self):
        return f'<Class Id: {self.id} | Subject: {self.subject} | Session: {self.session}>'

    def save(self, *args, **kwargs):
        self.num_level = self.set_num_level()
        super().save(*args, **kwargs)


class Profile(models.Model):
    """ Extending user model to have profile fields as appropriate as either a
        student or a staff member.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    bio = models.TextField(max_length=500, blank=True)
    level = models.IntegerField(verbose_name='skill level', default=0)
    taken = models.ManyToManyField(ClassOffer, related_name='students', through='Registration')
    # interest = models.ManyToManyField(Subject, related_names='interests', through='Requests')
    credit = models.FloatField(verbose_name='Class Payment Credit', default=0)
    # refer = models.ForeignKey(UserHC, symmetrical=False, on_delete=models.SET_NULL, null=True, blank=True, related_names='referred')
    date_added = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)

    # TODO: The following properties could be extracted further to allow the
    # program admin user to set their own rules for number of versions needed
    # and other version translation decisions.

    @property
    def highest_subject(self):
        """ We will want to know what is the student's class level
            which by default will be the highest class level they
            have taken. We also want to be able to override this
            from a teacher or admin input to deal with students
            who have had instruction or progress elsewhere.
        """
        # Query all taken ClassOffers for this student
        # ClassOffer.num_level is the level for each of these, find the max.
        # Currently returns max, Do we want LEVEL_CHOICES name of this max?
        have = [a.num_level for a in self.taken.all()]
        return max(have) if len(have) > 0 else 0

    @property
    def taken_subjects(self):
        """ Since all taken subjects are related through ClassOffer
            We will query taken classes to report taken subjects
        """
        subjs = [c.subject for c in self.taken.all()]
        # TODO: remove following print line once confirmed.
        print(subjs)
        return subjs

    @property
    def beg_finished(self):
        version_translate = {'A': 'A', 'B': 'B', 'C': 'A', 'D': 'B'}
        set_count = {'A': 0, 'B': 0}
        subjs = self.taken_subjects
        for subj in subjs:
            if subj.level == Subject.LEVEL_CHOICES[0][0]:  # 'Beg'
                ver = version_translate[subj.version]
                set_count[ver] += 1
        if set_count['A'] > 0 and set_count['B'] > 0:
            return True
        return False

    @property
    def l2_finished(self):
        set_count = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
        subjs = self.taken_subjects
        for subj in subjs:
            if subj.level == Subject.LEVEL_CHOICES[1][0]:  # 'L2'
                ver = subj.version
                set_count[ver] += 1
        if set_count['A'] > 0 and set_count['B'] > 0 and set_count['C'] > 0 and set_count['D'] > 0:
            return True
        return False

    def username(self):
        return self.user.username

    def __str__(self):
        return self.user.get_full_name()

    def __repr__(self):
        return self.user.get_full_name()

    @property
    def checkin_list(self):
        return [
            self.user.first_name,
            self.user.last_name,
            self.taken,
            self.credit,
        ]


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


class Registration(models.Model):
    """ This is an intermediary model refrienced by a user profile model
        so that we can see which students are enrolled in a ClassOffer
    """
    student = models.ForeignKey(Profile, on_delete=models.CASCADE)
    classoffer = models.ForeignKey(ClassOffer, on_delete=models.CASCADE)

    @property
    def first_name(self):
        return self.student.user.first_name

    @property
    def last_name(self):
        return self.student.user.last_name

    @property
    def credit(self):
        return self.student.credit

    @property
    def reg_class(self):
        return self.classoffer.subject.level
    # reg_class.admin_order_field = 'classoffer__subject__level'

    @property
    def reg_session(self):
        return self.classoffer.session.name
    # reg_session.admin_order_field = 'classoffer__session__key_day_date'

    # class Meta:
    #     order_with_respect_to = 'classoffer'
    #     pass

    # end class Registration


class Payment(BasePayment):
    """ Payment Processing
    """
    # variant = models.CharField(max_length=255)
    #: Transaction status
    # status = models.CharField(
    #     max_length=10, choices=PaymentStatus.CHOICES,
    #     default=PaymentStatus.WAITING)
    # fraud_status = models.CharField(
    #     _('fraud check'), max_length=10, choices=FraudStatus.CHOICES,
    #     default=FraudStatus.UNKNOWN)
    # fraud_message = models.TextField(blank=True, default='')
    # #: Creation date and time
    # created = models.DateTimeField(auto_now_add=True)
    # #: Date and time of last modification
    # modified = models.DateTimeField(auto_now=True)
    # #: Transaction ID (if applicable)
    # transaction_id = models.CharField(max_length=255, blank=True)
    # #: Currency code (may be provider-specific)
    # currency = models.CharField(max_length=10)
    # #: Total amount (gross)
    # total = models.DecimalField(max_digits=9, decimal_places=2, default='0.0')
    # delivery = models.DecimalField(
    #     max_digits=9, decimal_places=2, default='0.0')
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
    # captured_amount = models.DecimalField(
    #     max_digits=9, decimal_places=2, default='0.0')

    def get_failure_url(self):
        return 'http://example.com/failure/'

    def get_success_url(self):
        return 'http://example.com/success/'

    def get_purchased_items(self):
        # you'll probably want to retrieve these from an associated order
        yield PurchasedItem(name='The Hound of the Baskervilles', sku='BSKV',
                            quantity=9, price=Decimal(10), currency='USD')

    # end class Payment


# end models.py

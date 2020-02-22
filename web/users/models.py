from django.contrib.auth.models import AbstractUser, UserManager  # , Group
from django.db import models


def get_if_only_one(q, **kwargs):
    """ If it does not exist, or if there are many that match, return none """
    search = None
    if isinstance(q, models.QuerySet):
        search = q.filter(**kwargs)
    elif isinstance(q, models.Model):
        search = q.objects.filter(**kwargs)
    obj = search[0] if search and len(search) == 1 else None
    return obj

# Create your models here.
# TODO: Move some of the student vs staff logic to Group


class UserManagerHC(UserManager):
    """ Adding & Modifying some features to the default UserManager
        Inherits from: UserManager, BaseUserManager, models.Manager, ...
    """
    # from Django's UserManager
    # use_in_migrations = True

    def normalize_email(cls, email):
        """ While uppercase characters are technically allowed for the username
            portion of an email address, we are deciding to not allow uppercase
            characters with the understanding that many email systems do not
            respect uppercase as different from lowercase.
            Instead of calling .lower(), which is the default technique used
            by the UserManager, we are using .casefold(), which is better when
            dealing with some international character sets.
        """
        email = email or ''
        # email = super().normalize_email(email)
        try:
            email_name, domain_part = email.strip().rsplit('@', 1)
        except ValueError:
            pass
        else:
            email = email_name.casefold() + '@' + domain_part.casefold()
        return email

    def set_username(self, username=None, email=None, password=None, **extra_fields):
        """ This method is an inserted intermediary step before the inherited
            self._create_user method and after the normal user creation
            called methods of either create_user or create_superuser
        """
        from django.db.utils import IntegrityError
        print('===== UserManagerHC.set_username was called ========')
        email = self.normalize_email(email)
        user = None
        if extra_fields.get('uses_email_username') is True:
            if email is None:
                raise ValueError('You must either have a unique email address, or set a username')
            username = email
            try:
                user = self._create_user(username, email, password, **extra_fields)
            except IntegrityError:
                extra_fields.setdefault('uses_email_username', False)
        if extra_fields.get('uses_email_username') is False:
            temp = extra_fields.get('first_name') + '_' + extra_fields.get('last_name')
            username = temp.casefold()
            user = self._create_user(username, email, password, **extra_fields)
        return user

    def create_user(self, username=None, email=None, password=None, **extra_fields):
        print('================================')
        print('UserManagerHC method create_user method was called')
        extra_fields.setdefault('is_superuser', False)
        if extra_fields.get('is_teacher') is True or extra_fields.get('is_admin') is True:
            extra_fields.setdefault('is_staff', True)
        else:
            extra_fields.setdefault('is_staff', False)
            extra_fields.setdefault('is_student', True)
        return self.set_username(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.set_username(username, email, password, **extra_fields)

    def find_or_create_for_anon(self, email=None, possible_users=None, **kwargs):
        """ This is called when someone registers when they are not logged in.
            If they are a new customer, we want no friction, just create a
            user account. If they might be an existing user, we need to get
            them logged in.
        """
        first_name = kwargs.get('first_name')
        last_name = kwargs.get('last_name')
        if not kwargs.get('is_student') and not kwargs.get('is_teacher') and not kwargs.get('is_admin'):
            kwargs['is_student'] = True
        # if not possible_users:
        #     # assume we want to query all users
        #     possible_users = UserHC.objects.all()
        # if not isinstance(possible_users, models.QuerySet):
        #     print('possible_users is not a QuerySet')
        found = UserHC.objects.filter(email=email).count()
        found += UserHC.objects.filter(first_name=first_name, last_name=last_name).count()
        if found > 0:
            # redirect to login, auto-filling the appropriate fields
            # this login should also allow them to so say they don't have a user account.
            print('---- Maybe they have had classes before? -----')
            # TODO: redirect to the appropriate login
        else:
            # create a new user with this data
            print('----- Creating a new user! -----')
            return self.create_user(self, email=email, **kwargs)

        # end find_or_create_for_anon

    def find_or_create_by_name(self, email=None, possible_users=None, **kwargs):
        """ This is called when a user signs up someone else """
        first_name = kwargs.get('first_name')
        last_name = kwargs.get('last_name')
        # is_student = kwargs.get('is_student')
        print("======== UserHC.objects.find_or_create_by_name =====")
        if not possible_users:
            # assume we want to query all users
            possible_users = UserHC.objects.all()
        if not isinstance(possible_users, models.QuerySet):
            print('possible_users is not a QuerySet')
        print(possible_users)
        if len(possible_users) == 0:
            possible_users = None
        # TODO: Is this how we want to find matching or near matches?
        if possible_users:
            friend = get_if_only_one(possible_users, first_name=first_name, last_name=last_name) \
                or get_if_only_one(possible_users, first_name__icontains=first_name, last_name__icontains=last_name) \
                or get_if_only_one(possible_users, last_name__icontains=last_name) \
                or get_if_only_one(possible_users, first_name__icontains=first_name) \
                or get_if_only_one(UserHC, first_name=first_name, last_name=last_name) \
                or get_if_only_one(UserHC, first_name__icontains=first_name, last_name__icontains=last_name) \
                or None
            # TODO: Should there be some kind of confirmation page?
            if friend:
                return friend
        # Otherwise we create a new user and profile
        return self.create_user(self, email=email, **kwargs)

    # end class UserManagerHC


class UserHC(AbstractUser):
    """ This will be the custom Users model for the site
        Inherits from: AbstractUser, AbstractBaseUser, models.Model, ModelBase, ...
    """

    # is_superuser exists from inherited models.
    is_student = models.BooleanField('student', default=True)
    is_teacher = models.BooleanField('teacher', default=False)
    is_admin = models.BooleanField('admin', default=False)
    uses_email_username = models.BooleanField('Using Email', default=True)
    billing_address_1 = models.CharField(max_length=255, blank=True)
    billing_address_2 = models.CharField(max_length=255, blank=True)
    billing_city = models.CharField(max_length=255, blank=True)
    billing_country_area = models.CharField(max_length=2, default='WA', blank=True)  # State, if in US
    billing_postcode = models.CharField(max_length=255, blank=True)
    billing_country_code = models.CharField(max_length=2, default='US', blank=True)
    # # user.profile holds the linked profile for this user.
    objects = UserManagerHC()

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return self.username

    def make_username(self):
        """ Instead of user selecting a username, we will generate it from their
            info. We are using casefold() instead of lower() since it is
            better for some international character sets.
        """
        print('================================')
        print('UserHC method make_username was called')
        if self.uses_email_username is True:
            # TODO: How to check if their email is already taken as a username?
            return self.email.casefold()
        temp = self.first_name + '_' + self.last_name
        return temp.casefold()

    def save(self, *args, **kwargs):
        """ Take some actions before the actual saving of the instance
            is called with super().save(*args, **kwargs)
        """
        self.username = self.make_username()
        if self.is_teacher or self.is_admin or self.is_superuser:
            self.is_staff = True
        else:
            self.is_staff = False
        # TODO: Deal with username (email) being checked as existing even when we want a new user
        super().save(*args, **kwargs)

    # end class UserHC

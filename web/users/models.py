from django.contrib.auth.models import AbstractUser, UserManager  # , Group
from django.db import models
from django.utils.translation import gettext_lazy as _


def get_if_only_one(q, **kwargs):
    """ If it does not exist, or if there are many that match, return none """
    search = None
    if isinstance(q, models.QuerySet):
        search = q.filter(**kwargs)
    elif isinstance(q, models.Model):
        search = q.objects.filter(**kwargs)
    obj = search[0] if search and len(search) == 1 else None
    # TODO: Refactor to using better Django Query techniques.
    return obj

# TODO: Move some of the student vs staff logic to Group
# Create your models here.


class UserManagerHC(UserManager):
    """ Adding & Modifying some features to the default UserManager.
        Inherits from: UserManager, BaseUserManager, models.Manager, ...
    """
    # from Django's UserManager
    # use_in_migrations = True

    @staticmethod
    def normalize_email(email):
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

    def set_user(self, username=None, email=None, password=None, **extra_fields):
        """ Called for all user creation methods (create_user, create_superuser).
            Email addresses and login usernames are normalized, allowing no uppercase characters.
            A user must have a unique login username (usually their email address).
            Unless the 'uses_email_username' was explicitly set to False, we will use the email as username.
            If a user with that email already exists (or 'uses_email_username' is False), and no username was provided,
            then it will create one based on their 'first_name' and 'last_name'.
            Raises Error if a unique username cannot be formed, or otherwise cannot create the user.
            Returns a user instance created with the inherited self._create_user method if successful.
        """
        from django.db.utils import IntegrityError
        # print('===== UserManagerHC.set_user was called ========')
        user, message = None, ''
        if not email:
            message += "An email address is preferred to ensure confirmation, "
            message += "but we can create an account without one. "
            if extra_fields.setdefault('uses_email_username', False):
                message += "You requested to use email as your login username, but did not provide an email address. "
                raise ValueError(_(message))
        else:
            email = self.normalize_email(email)

        if extra_fields.setdefault('uses_email_username', True):
            attempt_username = email
            try:
                user = self._create_user(attempt_username, email, password, **extra_fields)
            except IntegrityError:
                message += "A unique email address is preferred, but a user already exists with that email address. "
                extra_fields['uses_email_username'] = False
        if extra_fields.get('uses_email_username') is False:
            username = username or extra_fields.get('first_name', '') + '_' + extra_fields.get('last_name', '')
            if username == '_':
                message += "If you are not using your email as your username/login, "
                message += "then you must either set a username or provide a first and last name. "
                raise ValueError(_(message))
            username = username.casefold()
            try:
                user = self._create_user(username, email, password, **extra_fields)
            except IntegrityError:
                message += "A user already exists with that username, or matching first and last name. "
                message += "Please provide some form of unique user information (email address, username, or name). "
                raise ValueError(_(message))
        return user

    def create_user(self, username=None, email=None, password=None, **extra_fields):
        # print('================== UserManagerHC.create_user ========================')
        extra_fields['is_superuser'] = False  # This method will never allow creating a superuser.
        if extra_fields.get('is_teacher') is True or extra_fields.get('is_admin') is True:
            extra_fields.setdefault('is_staff', True)
            extra_fields.setdefault('is_student', False)
        else:
            extra_fields.setdefault('is_staff', False)
            extra_fields.setdefault('is_student', True)
        return self.set_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        # print('================== UserManagerHC.create_superuser ========================')
        if not extra_fields.setdefault('is_staff', True):
            raise ValueError(_('Superuser must have is_staff=True.'))
        if not extra_fields.setdefault('is_superuser', True):
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.set_user(username, email, password, **extra_fields)

    def find_or_create_for_anon(self, email=None, possible_users=None, **kwargs):
        """ This is called when someone registers when they are not logged in. If they are a new customer, we want
            no friction, just create a user account. If they might be an existing user, we need to get them logged in.
        """
        first_name, last_name = kwargs.get('first_name'), kwargs.get('last_name')
        if not kwargs.get('is_student') and not kwargs.get('is_teacher') and not kwargs.get('is_admin'):
            kwargs['is_student'] = True
        found = UserHC.objects.filter(email=email).count()
        found += UserHC.objects.filter(first_name=first_name, last_name=last_name).count()
        if found > 0:
            # TODO: redirect to login, auto-filling appropriate fields. This should also work if they have no account.
            print('---- Maybe they have had classes before? -----')
        else:
            print('----- Creating a new user! -----')
            return self.create_user(self, email=email, **kwargs)  # create a new user with this data
        # end find_or_create_for_anon

    def find_or_create_by_name(self, email=None, possible_users=None, **kwargs):
        """ This is called when a user signs up someone else """
        first_name, last_name = kwargs.get('first_name'), kwargs.get('last_name')
        # print("======== UserHC.objects.find_or_create_by_name =====")
        if not possible_users:  # assume we want to query all users
            possible_users = UserHC.objects.all()
        if not isinstance(possible_users, models.QuerySet):
            raise TypeError(_('Possible_users is not a QuerySet'))
        # TODO: Is this how we want to find matching or near matches?
        friend = get_if_only_one(possible_users, first_name=first_name, last_name=last_name) \
            or get_if_only_one(possible_users, first_name__icontains=first_name, last_name__icontains=last_name) \
            or get_if_only_one(possible_users, last_name__icontains=last_name) \
            or get_if_only_one(possible_users, first_name__icontains=first_name) \
            or get_if_only_one(UserHC, first_name=first_name, last_name=last_name) \
            or get_if_only_one(UserHC, first_name__icontains=first_name, last_name__icontains=last_name) \
            or None
        # TODO: Should there be some kind of confirmation page?
        # Otherwise we create a new user and profile
        return friend if friend else self.create_user(self, email=email, **kwargs)

    # end class UserManagerHC


class UserHC(AbstractUser):
    """ This will be the custom Users model for the site
        Inherits from: AbstractUser, AbstractBaseUser, models.Model, ModelBase, ...
    """

    # first_name, last_name, id, email, and username (often not used directly) - all exist from inherited models.
    is_student = models.BooleanField('student', default=True)
    is_teacher = models.BooleanField('teacher', default=False)
    is_admin = models.BooleanField('admin', default=False)
    # is_superuser exists from inherited models.
    # is_staff exists from inherited models.
    uses_email_username = models.BooleanField('Using Email', default=True)
    billing_address_1 = models.CharField(verbose_name='Street Address (line 1)', max_length=191, blank=True)
    billing_address_2 = models.CharField(verbose_name='Street Address (continued)', max_length=191, blank=True)
    billing_city = models.CharField(verbose_name='City', max_length=191, blank=True)
    billing_country_area = models.CharField(verbose_name='State', max_length=2, default='WA', blank=True,
                                            help_text='State, Territory, or Province')
    billing_postcode = models.CharField(verbose_name='Zip Code', max_length=191, blank=True,
                                        help_text='Zip or Postal Code')
    billing_country_code = models.CharField(verbose_name='Country', default='USA', max_length=191, blank=True)
    # # # user.profile holds the linked profile for this user.
    objects = UserManagerHC()

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        name = self.get_full_name() or self.username  # _("Name Not Found")
        return name

    def make_username(self):
        """ Instead of user selecting a username, we will generate it from their
            info. We are using casefold() instead of lower() since it is
            better for some international character sets.
        """
        # print('================================')
        # print('UserHC method make_username was called')
        if self.uses_email_username is True:
            # TODO: How to check if their email is already taken as a username?
            return self.email.casefold()
        temp = self.first_name + '_' + self.last_name
        return temp.casefold()

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.make_username()
        if self.is_teacher or self.is_admin or self.is_superuser:
            self.is_staff = True
        else:
            self.is_staff = False
        # TODO: Deal with username (email) being checked as existing even when we want a new user
        super().save(*args, **kwargs)

    # end class UserHC

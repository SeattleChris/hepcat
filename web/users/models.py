from django.contrib.auth.models import AbstractUser, UserManager  # , Group
from django.db import models
from classwork.models import Subject
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.


class UserManagerHC(UserManager):
    """ Adding & Modifying some features to the default UserManager
        Inherits from: UserManager, BaseUserManager, models.Manager, ...
    """

    def normalize_email(cls, email):
        """ We are still depending on normalize_email method from BaseUserManager.
            If we experience problems from .lower() call it uses, we can switch
            email to the commented code below and bypass the default method.
        """
        # email = email or ''
        email = super().normalize_email(email)
        try:
            email_name, domain_part = email.strip().rsplit('@', 1)
        except ValueError:
            pass
        else:
            email = email_name.casefold() + '@' + domain_part.casefold()
        return email

    # from Django's UserManager
    # use_in_migrations = True

    # def _create_user(self, username, email, password, **extra_fields):
    #     """
    #     Create and save a user with the given username, email, and password.
    #     """
    #     if not username:
    #         raise ValueError('The given username must be set')
    #     email = self.normalize_email(email)
    #     username = self.model.normalize_username(username)
    #     user = self.model(username=username, email=email, **extra_fields)
    #     user.set_password(password)
    #     user.save(using=self._db)
    #     return user

    def create_user(self, username=None, email=None, password=None, **extra_fields):
        from django.db.utils import IntegrityError

        extra_fields.setdefault('is_superuser', False)
        if extra_fields.get('is_teacher') is True or extra_fields.get('is_admin') is True:
            extra_fields.setdefault('is_staff', True)
        else:
            extra_fields.setdefault('is_staff', False)
        user = ''
        if extra_fields.get('uses_email_username') is True:
            if email is None:
                raise ValueError('You must either have a unique email address, or set a username')
            username = email
            try:
                user = self._create_user(username, email, password, **extra_fields)
            except IntegrityError:
                extra_fields.setdefault('uses_email_username', False)
                # user = self._create_user('fakeout', email, password, **extra_fields)
        if extra_fields.get('uses_email_username') is False:
            temp = extra_fields.get('first_name') + '_' + extra_fields.get('last_name')
            username = temp.casefold()
            user = self._create_user(username, email, password, **extra_fields)
        return user
        # return self._create_user(username, email, password, **extra_fields)

    # def create_superuser(self, username, email, password, **extra_fields):
    #     extra_fields.setdefault('is_staff', True)
    #     extra_fields.setdefault('is_superuser', True)

    #     if extra_fields.get('is_staff') is not True:
    #         raise ValueError('Superuser must have is_staff=True.')
    #     if extra_fields.get('is_superuser') is not True:
    #         raise ValueError('Superuser must have is_superuser=True.')

    #     return self._create_user(username, email, password, **extra_fields)


class UserHC(AbstractUser):
    """ This will be the custom Users model for the site
        Inherits from: AbstractUser, AbstractBaseUser, models.Model, ModelBase, ...
    """
    is_student = models.BooleanField('student', default=True)
    is_teacher = models.BooleanField('teacher', default=False)
    is_admin = models.BooleanField('admin', default=False)
    uses_email_username = models.BooleanField('Using Email', default=True)
    # USERNAME_FIELD = 'email'
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


class Profile(models.Model):
    """ Extending user model to have profile fields as appropriate as either a
        student or a staff member.
    """
    user = models.OneToOneField(UserHC, on_delete=models.CASCADE, primary_key=True)
    bio = models.TextField(max_length=500, blank=True)
    level = models.IntegerField(verbose_name='skill level', default=0)
    taken = models.ManyToManyField(Subject)  # TODO: ADD related_name='students'
    # taken = models.ManyToManyField(Subject, through=TakenSubject)
    # interest = models.ManyToManyField(Subject, related_names='interests')
    # interest = models.ManyToManyField(Subject, through=InterestSubject)
    credit = models.FloatField(verbose_name='Class Payment Credit', default=0)
    # refer = models.ForeignKey(UserHC, symmetrical=False, on_delete=models.SET_NULL, null=True, blank=True, related_names='referred')

    @property
    def highest_subject(self):
        """ We will want to know what is the student's class level
            which by default will be the highest class level they
            have taken. We also want to be able to override this
            from a teacher or admin input to deal with students
            who have had instruction or progress elsewhere.
        """
        # Query all taken subjects for this student
        # Subject.num_level is the level for each of these, find the max.
        # return the Subject.level of this max Subject.num_level
        # taken_subjects = self.taken.all()
        have = [subj.num_level for subj in self.taken.all()]
        return max(have) if len(have) > 0 else 0

    def username(self):
        return self.user.username

    def __str__(self):
        return self.user.get_full_name()


@receiver(post_save, sender=UserHC)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


class Staff(models.Model):
    """ Extending user model to have the fields unique to on staff Teachers
        We want an image, a bio, and a connection to classes they taught
    """
    user = models.OneToOneField(UserHC, on_delete=models.CASCADE, primary_key=True)
    bio = models.TextField(max_length=500, blank=True)
    # headshot = models.ImageField()
    # set is_staff to True

    def __str__(self):
        return self.user.get_full_name()


class Student(models.Model):
    """ Extending user model for students to track what classes they have
        taken, and associate resources they have access to view.
    """
    user = models.OneToOneField(UserHC, on_delete=models.CASCADE, primary_key=True)
    level = models.IntegerField(verbose_name='Student Skill Level Number', default=0)
    taken = models.ManyToManyField(Subject)
    # taken = models.ManyToManyField(Subject, through=TakenSubject)
    # interest = models.ManyToManyField(Subject, related_names='interests')
    # interest = models.ManyToManyField(Subject, through=InterestSubject)
    credit = models.FloatField(verbose_name='Class Payment Credit', default=0)
    # refer = models.ForeignKey(UserHC, symmetrical=False, on_delete=models.SET_NULL, null=True, blank=True, related_names='referred')

    def highest_subject(self):
        """ We will want to know what is the student's class level
            which by default will be the highest class level they
            have taken. We also want to be able to override this
            from a teacher or admin input to deal with students
            who have had instruction or progress elsewhere.
        """
        pass

    def __str__(self):
        return self.user.first_name + self.user.last_name


# @receiver(post_save, sender=UserHC)
# def create_or_update_user_profile(sender, instance, created, **kwargs):
#     if instance.is_student:
#         if created:
#             Student.objects.create(user=instance)
#         instance.Student.save()
#     if instance.is_teacher or instance.is_admin:
#         if created:
#             Staff.objects.create(user=instance)
#         instance.Staff.save()






# class TakenSubject(models.Model):
#     """ This table associates users with which class Subjects they
#         have already had
#     """
#     # TODO: Make this association table?
#     student = models.ForeignKey(Student, on_delete=models.CASCADE)
#     subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
#     date_added = models.DateField(auto_now_add=True)

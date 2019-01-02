from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from classwork.models import Subject
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.


class UserHC(AbstractUser):
    """ This will be the custom Users model for the site
    """
    is_student = models.BooleanField('student', default=True)
    is_teacher = models.BooleanField('teacher', default=False)
    is_admin = models.BooleanField('admin', default=False)
    uses_email_username = models.BooleanField('Using Email', default=True)

    def get_short_name(self):
        """ Replaces the username in greetings to the user in the header of admin
        """
        return self.first_name.capitalize()

    def get_full_name(self):
        """ Formal identifier for user, appears alongside username in object history
        """
        return self.first_name.capitalize() + ' ' + self.last_name.capitalize()

    def __str__(self):
        return self.email

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
        if self.is_teacher or self.is_admin:
            self.is_staff = True
        super().save(*args, **kwargs)


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


@receiver(post_save, sender=UserHC)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if instance.is_student:
        if created:
            Student.objects.create(user=instance)
        instance.Student.save()
    if instance.is_teacher or instance.is_admin:
        if created:
            Staff.objects.create(user=instance)
        instance.Staff.save()






# class TakenSubject(models.Model):
#     """ This table associates users with which class Subjects they
#         have already had
#     """
#     # TODO: Make this association table?
#     student = models.ForeignKey(Student, on_delete=models.CASCADE)
#     subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
#     date_added = models.DateField(auto_now_add=True)

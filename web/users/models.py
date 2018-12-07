from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class UserHC(AbstractUser):
    """ This will be the custom Users model for the site
    """
    uses_email_username = models.BooleanField(default=True)

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
        # Probably should change this to pre_save signal
        self.username = self.make_username()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


# class Profile(UserHC):
#     """ We seperate some of the User info into the Profile
#     """
#     user = models.ForeignKey(UserHC, on_delete=models.CASCADE)

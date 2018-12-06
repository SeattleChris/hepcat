from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class UserHC(AbstractUser):
    """ This will be the custom Users model for the site
    """
    # uses_alt_username = False

    # def make_username(self):
    #     """ Instead of user selecting a username, we will generate it from their info
    #     """
    #     pass

    def __str__(self):
        return self.email

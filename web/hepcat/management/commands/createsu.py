from django.core.management.base import BaseCommand  # , CommandError
# from django.contrib.auth.models import User
import os
from django.conf import settings  # User = settings.AUTH_USER_MODEL
from django.contrib.auth import get_user_model
User = get_user_model()


class Command(BaseCommand):
    """ Allows the creation of a superuser with a password set in the environment variables. """

    def handle(self, *args, **options):
        self.stderr.write("================================================")
        self.stderr.write(f"========== Make SUPERUSER =====================")
        if not User.objects.filter(is_superuser="t").exists():
            self.stderr.write("This is the FIRST SuperUser. ")
        else:
            self.stderr.write("At least one SuperUser already existed. ")
        username = os.environ.get('SUPERUSER_NAME', settings.ADMINS[0][0])
        email = os.environ.get('SUPERUSER_EMAIL', settings.ADMINS[0][1])
        password = os.environ.get('SUPERUSER_PASS', None)
        self.stderr.write(f"username: {username}, email: {email}, pw: {password}")
        if not User.objects.filter(email=email).exists():
            user = User.objects.create_superuser(username, email, password)
            self.stderr.write(user)
        else:
            self.stderr.write("A user already exists with that email address. ")

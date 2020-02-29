from django.core.management.base import BaseCommand  # , CommandError
# from django.contrib.auth.models import User
import os
from django.conf import settings  # User = settings.AUTH_USER_MODEL
from django.contrib.auth import get_user_model
User = get_user_model()


class Command(BaseCommand):
    """ Allows the creation of a superuser with a password set in the environment variables. """

    def handle(self, *args, **options):
        self.stdout.write(f"========== Make SUPERUSER =====================")
        # username = os.environ.get('SUPERUSER_NAME', settings.ADMINS[0][0])
        email = os.environ.get('SUPERUSER_EMAIL', settings.ADMINS[0][1])
        username = email.casefold()
        password = os.environ.get('SUPERUSER_PASS', None)
        self.stdout.write(f"username: {username}, email: {email}, pw: {password}")
        if not User.objects.filter(username=username).exists():
            try:
                user = User.objects.create_superuser(username, email, password)
                self.stdout.write(str(user))
            except Exception as e:
                self.stderr.write(f"Error: {e} ")
        else:
            self.stdout.write('That user already existed. ')

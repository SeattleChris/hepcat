from django.core.management.base import BaseCommand  # , CommandError
# from django.contrib.auth.models import User
import os
from django.conf import settings  # User = settings.AUTH_USER_MODEL
from django.contrib.auth import get_user_model
User = get_user_model()


class Command(BaseCommand):
    """Allows the creation of a superuser with a password set in the environment variables. """

    def handle(self, *args, **options):
        # TODO: Determine the print command: self.stdout.write worked on AWS, printed but error on PythonAnywhere.
        self.stdout.write("========== Make SUPERUSER =====================")
        # username = os.environ.get('SUPERUSER_NAME', settings.ADMINS[0][0])
        first_name = os.environ.get('SUPERUSER_FIRST_NAME', None)
        last_name = os.environ.get('SUPERUSER_LAST_NAME', None)
        email = os.environ.get('SUPERUSER_EMAIL', None)
        if not email:
            (first_name, email) = settings.ADMINS[0] if not first_name else (first_name, settings.ADMINS[0][1])
        password = os.environ.get('SUPERUSER_PASS', None)
        username = email or first_name or last_name
        extra_fields = {'first_name': first_name, 'last_name': last_name}
        self.stdout.write(f"username: {username}, email: {email}, pw: {password}")
        if not User.objects.filter(username=username).exists():
            try:
                user = User.objects.create_superuser(username, email, password, **extra_fields)
                self.stdout.write(str(user))
            except Exception as e:
                self.stderr.write(f"Error: {e} ")
        else:
            self.stdout.write('That user already existed. ')

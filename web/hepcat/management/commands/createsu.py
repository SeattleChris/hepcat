from django.core.management.base import BaseCommand  # , CommandError
# from django.contrib.auth.models import User
import os
from django.conf import settings  # User = settings.AUTH_USER_MODEL
from django.contrib.auth import get_user_model
User = get_user_model()


class Command(BaseCommand):

    def handle(self, *args, **options):
        if not User.objects.filter(is_superuser="t").exists():
            username = os.environ.get('SUPERUSER_NAME', settings.ADMINS[0][0])
            email = os.environ.get('SUPERUSER_EMAIL', settings.ADMINS[0][1])
            password = os.environ.get('SUPERUSER_PASS', None)
            self.stdout.write("================================================")
            self.stdout.write(f"========== Make SUPERUSER =====================")
            self.stdout.write(f"username: {username}, email: {email}, pw: {password}")
            User.objects.create_superuser(username, email, password)

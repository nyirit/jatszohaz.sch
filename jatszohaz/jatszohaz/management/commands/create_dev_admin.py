from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from jatszohaz.models import JhUser


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            JhUser.objects.create_superuser('admin', 'admin@example.com', 'admin')
            self.stdout.write(self.style.SUCCESS("Superuser created: admin/admin"))

            JhUser.objects.create_user('user', 'user@example.com', 'user')
            self.stdout.write(self.style.SUCCESS("User created: user/user"))
        except IntegrityError:
            self.stdout.write(self.style.SUCCESS("Superuser with username admin already exists."))

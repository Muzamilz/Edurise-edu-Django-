from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session

class Command(BaseCommand):
    help = 'Clears all sessions from the database'

    def handle(self, *args, **options):
        count = Session.objects.count()
        Session.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Successfully cleared {count} sessions')) 
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Create superusers with predefined details and permissions.'

    def handle(self, *args, **options):
        User = get_user_model()
        superusers = [
            {
                'email': 'superadmin@edurise.com',
                'username': 'superadmin',
                'password': 'SuperAdmin@123',
                'first_name': 'Super',
                'last_name': 'Admin',
            },
            {
                'email': 'contentadmin@edurise.com',
                'username': 'contentadmin',
                'password': 'ContentAdmin@123',
                'first_name': 'Content',
                'last_name': 'Admin',
            },
            {
                'email': 'supportadmin@edurise.com',
                'username': 'supportadmin',
                'password': 'SupportAdmin@123',
                'first_name': 'Support',
                'last_name': 'Admin',
            },
        ]

        for su in superusers:
            if not User.objects.filter(email=su['email']).exists():
                user = User.objects.create_superuser(
                    email=su['email'],
                    username=su['username'],
                    password=su['password'],
                    first_name=su.get('first_name', ''),
                    last_name=su.get('last_name', ''),
                )
                user.is_superuser = True
                user.is_staff = True
                user.role = 'admin'
                user.is_approved = True
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Created superuser: {su['email']}"))
            else:
                self.stdout.write(self.style.WARNING(f"Superuser already exists: {su['email']}")) 
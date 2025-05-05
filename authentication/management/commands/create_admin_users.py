from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates admin users with specific roles and permissions'

    def handle(self, *args, **options):
        # Define admin users with their roles and permissions
        admin_users = [
            {
                'email': 'superadmin@edurise.com',
                'username': 'superadmin',
                'password': 'SuperAdmin@123',
                'first_name': 'Super',
                'last_name': 'Admin',
                'role': 'admin',
                'is_superuser': True,
                'is_staff': True,
                'is_active': True,
                'is_approved': True
            },
            {
                'email': 'contentadmin@edurise.com',
                'username': 'contentadmin',
                'password': 'ContentAdmin@123',
                'first_name': 'Content',
                'last_name': 'Admin',
                'role': 'admin',
                'is_superuser': False,
                'is_staff': True,
                'is_active': True,
                'is_approved': True
            },
            {
                'email': 'supportadmin@edurise.com',
                'username': 'supportadmin',
                'password': 'SupportAdmin@123',
                'first_name': 'Support',
                'last_name': 'Admin',
                'role': 'admin',
                'is_superuser': False,
                'is_staff': True,
                'is_active': True,
                'is_approved': True
            }
        ]

        # Create or update admin users
        for user_data in admin_users:
            try:
                user, created = User.objects.update_or_create(
                    email=user_data['email'],
                    defaults={
                        'username': user_data['username'],
                        'first_name': user_data['first_name'],
                        'last_name': user_data['last_name'],
                        'role': user_data['role'],
                        'is_superuser': user_data['is_superuser'],
                        'is_staff': user_data['is_staff'],
                        'is_active': user_data['is_active'],
                        'is_approved': user_data['is_approved']
                    }
                )
                user.set_password(user_data['password'])
                user.save()

                if created:
                    self.stdout.write(self.style.SUCCESS(f'Successfully created {user_data["role"]} user: {user_data["email"]}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Successfully updated {user_data["role"]} user: {user_data["email"]}'))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating/updating {user_data["email"]}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('Admin user creation process completed!')) 
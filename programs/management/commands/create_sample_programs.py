from django.core.management.base import BaseCommand
from django.utils import timezone
from programs.models import EducationalProgram
from authentication.models import User
from decimal import Decimal

class Command(BaseCommand):
    help = 'Create sample educational programs'

    def handle(self, *args, **kwargs):
        # Create a teacher if none exists
        teacher, created = User.objects.get_or_create(
            email='teacher@edurise.com',
            defaults={
                'username': 'teacher@edurise.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'role': 'teacher',
                'is_active': True,
                'is_approved': True
            }
        )
        if created:
            teacher.set_password('teacher123')
            teacher.save()

        # Sample programs data
        programs_data = [
            {
                'title': 'Regular English Program',
                'description': 'A comprehensive English language program covering all essential skills: reading, writing, speaking, and listening.',
                'program_type': 'regular_english',
                'level': 'beginner',
                'duration': '12 weeks',
                'price': Decimal('299.99'),
                'instructor': teacher,
                'status': 'published',
                'start_date': timezone.now(),
                'end_date': timezone.now() + timezone.timedelta(weeks=12)
            },
            {
                'title': 'Plus English Program',
                'description': 'An intensive English program with additional focus on business communication and academic writing.',
                'program_type': 'plus_english',
                'level': 'intermediate',
                'duration': '16 weeks',
                'price': Decimal('399.99'),
                'instructor': teacher,
                'status': 'published',
                'start_date': timezone.now(),
                'end_date': timezone.now() + timezone.timedelta(weeks=16)
            },
            {
                'title': 'IELTS Preparation',
                'description': 'Comprehensive preparation for the IELTS exam, including practice tests and exam strategies.',
                'program_type': 'test_prep',
                'level': 'advanced',
                'duration': '8 weeks',
                'price': Decimal('499.99'),
                'instructor': teacher,
                'status': 'published',
                'start_date': timezone.now(),
                'end_date': timezone.now() + timezone.timedelta(weeks=8)
            },
            {
                'title': 'Business English',
                'description': 'Specialized English program focusing on business communication, presentations, and negotiations.',
                'program_type': 'esp',
                'level': 'intermediate',
                'duration': '10 weeks',
                'price': Decimal('449.99'),
                'instructor': teacher,
                'status': 'published',
                'start_date': timezone.now(),
                'end_date': timezone.now() + timezone.timedelta(weeks=10)
            },
            {
                'title': 'Academic English (EAP)',
                'description': 'English for Academic Purposes program designed for university students and researchers.',
                'program_type': 'eap',
                'level': 'advanced',
                'duration': '14 weeks',
                'price': Decimal('549.99'),
                'instructor': teacher,
                'status': 'published',
                'start_date': timezone.now(),
                'end_date': timezone.now() + timezone.timedelta(weeks=14)
            }
        ]

        # Create programs
        for program_data in programs_data:
            program, created = EducationalProgram.objects.get_or_create(
                title=program_data['title'],
                defaults=program_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created program: {program.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'Program already exists: {program.title}')) 
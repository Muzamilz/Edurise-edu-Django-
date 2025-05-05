import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edurise.settings')
django.setup()

from django.utils import timezone
from authentication.models import Term
from datetime import timedelta

def create_terms():
    # Clear existing terms
    Term.objects.all().delete()

    # Create terms
    terms = [
        {
            'name': 'Term 1',
            'start_date': timezone.now().date(),
            'end_date': timezone.now().date() + timedelta(days=90),
            'weeks_off': [5, 10],
            'is_current': True,
            'is_next': False
        },
        {
            'name': 'Term 2',
            'start_date': timezone.now().date() + timedelta(days=91),
            'end_date': timezone.now().date() + timedelta(days=180),
            'weeks_off': [5, 10],
            'is_current': False,
            'is_next': True
        },
        {
            'name': 'Term 3',
            'start_date': timezone.now().date() + timedelta(days=181),
            'end_date': timezone.now().date() + timedelta(days=270),
            'weeks_off': [5, 10],
            'is_current': False,
            'is_next': False
        },
        {
            'name': 'Term 4',
            'start_date': timezone.now().date() + timedelta(days=271),
            'end_date': timezone.now().date() + timedelta(days=360),
            'weeks_off': [5, 10],
            'is_current': False,
            'is_next': False
        },
        {
            'name': 'Term 5',
            'start_date': timezone.now().date() + timedelta(days=361),
            'end_date': timezone.now().date() + timedelta(days=450),
            'weeks_off': [5, 10],
            'is_current': False,
            'is_next': False
        }
    ]

    for term_data in terms:
        term = Term.objects.create(**term_data)
        print(f"Created {term.name} from {term.start_date} to {term.end_date}")

if __name__ == '__main__':
    create_terms() 
from django import template
from django.utils import timezone
from programs.models import EducationalProgram, Lesson
from enrollments.models import Enrollment

register = template.Library()

@register.filter
def get_program_progress(enrollment):
    """Calculate the progress percentage for a program enrollment."""
    if not enrollment or not enrollment.program:
        return 0
    
    total_lessons = enrollment.program.lessons.count()
    if total_lessons == 0:
        return 0
    
    completed_lessons = enrollment.program.lessons.filter(
        lessonprogress__student=enrollment.student,
        lessonprogress__is_completed=True
    ).count()
    
    return (completed_lessons / total_lessons) * 100

@register.filter
def get_program_status_class(status):
    """Return the appropriate CSS class for a program status."""
    status_classes = {
        'draft': 'bg-secondary',
        'active': 'bg-success',
        'completed': 'bg-info',
        'archived': 'bg-danger'
    }
    return status_classes.get(status, 'bg-secondary')

@register.filter
def get_enrollment_status_class(status):
    """Return the appropriate CSS class for an enrollment status."""
    status_classes = {
        'pending': 'bg-warning',
        'approved': 'bg-success',
        'rejected': 'bg-danger',
        'in_progress': 'bg-info',
        'completed': 'bg-primary'
    }
    return status_classes.get(status, 'bg-secondary')

@register.filter
def format_duration(minutes):
    """Format duration in minutes to a readable string."""
    if not minutes:
        return "Not specified"
    
    hours = minutes // 60
    remaining_minutes = minutes % 60
    
    if hours > 0:
        if remaining_minutes > 0:
            return f"{hours}h {remaining_minutes}m"
        return f"{hours}h"
    return f"{remaining_minutes}m"

@register.filter
def get_upcoming_lessons(program, limit=5):
    """Get upcoming lessons for a program."""
    return program.lessons.filter(
        scheduled_date__gte=timezone.now()
    ).order_by('scheduled_date')[:limit]

@register.filter
def get_active_enrollments(program):
    """Get active enrollments for a program."""
    return program.enrollments.filter(
        status__in=['approved', 'in_progress']
    ).count()

@register.filter
def get_completed_enrollments(program):
    """Get completed enrollments for a program."""
    return program.enrollments.filter(status='completed').count()

@register.filter
def get_average_rating(program):
    """Calculate the average rating for a program."""
    ratings = program.ratings.values_list('rating', flat=True)
    if not ratings:
        return 0
    return sum(ratings) / len(ratings) 
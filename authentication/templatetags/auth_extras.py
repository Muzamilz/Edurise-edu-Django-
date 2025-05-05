from django import template

register = template.Library()

@register.filter
def status_color(status):
    """Return Bootstrap color class based on enrollment status."""
    color_map = {
        'pending': 'warning',
        'approved': 'success',
        'rejected': 'danger',
        'completed': 'info',
        'in_progress': 'primary',
    }
    return color_map.get(status, 'secondary')

@register.filter
def role_color(role):
    """
    Returns the appropriate Bootstrap color class for a user role.
    """
    color_map = {
        'student': 'primary',
        'teacher': 'success',
        'admin': 'danger'
    }
    return color_map.get(role, 'secondary') 
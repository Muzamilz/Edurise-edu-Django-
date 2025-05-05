from django import template

register = template.Library()

@register.filter
def role_color(role):
    """
    Returns the appropriate Bootstrap color class based on the user's role.
    """
    role_colors = {
        'admin': 'danger',
        'teacher': 'primary',
        'student': 'success',
        'staff': 'info',
        'parent': 'warning',
    }
    return role_colors.get(role.lower(), 'secondary') 
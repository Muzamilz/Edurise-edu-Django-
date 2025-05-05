from django import template

register = template.Library()

@register.filter
def status_color(status):
    color_map = {
        'pending': 'warning',
        'approved': 'success',
        'rejected': 'danger',
        'completed': 'info'
    }
    return color_map.get(status, 'secondary') 
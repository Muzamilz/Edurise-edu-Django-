from django import template

register = template.Library()

@register.filter
def filter_status(progress, status):
    return [p for p in progress if p.status == status]

@register.filter
def get_lesson(progress, lesson):
    return next((p for p in progress if p.lesson == lesson), None) 
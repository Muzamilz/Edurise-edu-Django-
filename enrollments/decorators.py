from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.shortcuts import redirect

def teacher_required(view_func):
    """
    Decorator for views that checks that the user is a teacher,
    redirecting to the login page if necessary.
    """
    def check_teacher(user):
        if not user.is_authenticated:
            return False
        if user.role != 'teacher':
            messages.error(user, 'You must be a teacher to access this page.')
            raise PermissionDenied
        return True

    return user_passes_test(check_teacher)(view_func) 
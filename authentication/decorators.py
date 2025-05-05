from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied


def student_required(view_func):
    """
    Decorator for views that checks that the logged-in user is a student.
    Redirects to login if not authenticated, or raises PermissionDenied if not a student.
    """
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        if getattr(request.user, 'role', None) != 'student':
            raise PermissionDenied("You must be a student to access this page.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def teacher_required(view_func):
    """
    Decorator for views that checks that the logged-in user is a teacher.
    Redirects to login if not authenticated, or raises PermissionDenied if not a teacher.
    """
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        if getattr(request.user, 'role', None) != 'teacher':
            raise PermissionDenied("You must be a teacher to access this page.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

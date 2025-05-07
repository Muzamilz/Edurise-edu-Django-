from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Count, Avg, Sum, Q
from django.core.paginator import Paginator
import csv
import psutil
import json
from datetime import timedelta
from .models import (
    UserActivityLog, UserPermission, UserSession, SystemHealthLog,
    ErrorLog, APILog, AnalyticsReport, AnalyticsData, AdminSetting,
    AdminAuditLog, Announcement, AnnouncementCategory
)
from authentication.models import User, FAQ
from enrollments.models import Enrollment
from zoom_integration.models import ZoomMeeting, VirtualClass
from authentication.forms import UserRegistrationForm
from .forms import AdminUserCreationForm
from blog.models import BlogPost, Comment
from programs.models import EducationalProgram, Course, ProgramRating, LessonProgress
from django.contrib.auth.models import Group, Permission

def is_superadmin(user):
    return user.is_authenticated and user.role == 'admin' and user.is_superuser

def is_admin(user):
    return user.is_authenticated and user.is_staff

# Advanced User Management Views
@login_required
@user_passes_test(is_superadmin)
def user_activity_logs(request):
    logs = UserActivityLog.objects.select_related('user').order_by('-timestamp')
    
    # Filtering
    action = request.GET.get('action')
    if action:
        logs = logs.filter(action=action)
    
    # Pagination
    paginator = Paginator(logs, 50)
    page = request.GET.get('page', 1)
    logs_page = paginator.get_page(page)
    
    context = {
        'logs': logs_page,
        'page_title': 'User Activity Logs',
    }
    return render(request, 'admin_tools/user_activity.html', context)

@login_required
@user_passes_test(is_superadmin)
def user_permissions(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        permission = request.POST.get('permission')
        action = request.POST.get('action')
        
        user = get_object_or_404(User, id=user_id)
        if action == 'grant':
            UserPermission.objects.create(
                user=user,
                permission_name=permission,
                granted_by=request.user
            )
            messages.success(request, f'Permission {permission} granted to {user.email}')
        elif action == 'revoke':
            UserPermission.objects.filter(
                user=user,
                permission_name=permission
            ).delete()
            messages.success(request, f'Permission {permission} revoked from {user.email}')
    
    users = User.objects.prefetch_related('permissions').all()
    # Fetch all groups and annotate with user count
    groups = Group.objects.all()
    for group in groups:
        group.user_count = group.user_set.count()
    # Fetch all roles (distinct user roles)
    roles = []
    for role_name in User.objects.values_list('role', flat=True).distinct():
        if role_name:
            role_obj = type('Role', (), {})()
            role_obj.name = role_name
            role_obj.permissions = Permission.objects.filter(group__user__role=role_name).distinct()
            role_obj.user_count = User.objects.filter(role=role_name).count()
            roles.append(role_obj)
    # All available permissions
    available_permissions = Permission.objects.all()
    context = {
        'users': users,
        'roles': roles,
        'groups': groups,
        'available_permissions': available_permissions,
        'page_title': 'User Permissions',
    }
    return render(request, 'admin_tools/permissions.html', context)

@login_required
@user_passes_test(is_superadmin)
def user_sessions(request):
    if request.method == 'POST':
        session_id = request.POST.get('session_id')
        session = get_object_or_404(UserSession, id=session_id)
        session.is_active = False
        session.save()
        messages.success(request, f'Session terminated for {session.user.email}')
    
    active_sessions = UserSession.objects.filter(
        is_active=True
    ).select_related('user').order_by('-last_activity')
    
    context = {
        'active_sessions': active_sessions,
        'page_title': 'Active User Sessions',
    }
    return render(request, 'admin_tools/sessions.html', context)

@login_required
@user_passes_test(is_admin)
def bulk_user_operations(request):
    """View for performing bulk operations on users."""
    if request.method == 'POST':
        operation = request.POST.get('operation')
        user_ids = request.POST.getlist('user_ids')
        
        if not user_ids:
            messages.error(request, 'Please select at least one user.')
            return redirect('admin_tools:bulk_user_operations')
        
        users = User.objects.filter(id__in=user_ids)
        
        if operation == 'activate':
            users.update(is_active=True)
            messages.success(request, f'Successfully activated {users.count()} users.')
            
        elif operation == 'deactivate':
            users.update(is_active=False)
            messages.success(request, f'Successfully deactivated {users.count()} users.')
            
        elif operation == 'delete':
            # Log the deletion before performing it
            for user in users:
                AdminAuditLog.objects.create(
                    admin=request.user,
                    action='bulk_delete_user',
                    entity_type='User',
                    entity_id=str(user.id),
                    details=f'Bulk deleted user: {user.email}'
                )
            users.delete()
            messages.success(request, f'Successfully deleted {len(user_ids)} users.')
            
        elif operation == 'export':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="users.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['Email', 'First Name', 'Last Name', 'Role', 'Date Joined', 'Last Login', 'Status'])
            
            for user in users:
                writer.writerow([
                    user.email,
                    user.first_name,
                    user.last_name,
                    user.role,
                    user.date_joined,
                    user.last_login,
                    'Active' if user.is_active else 'Inactive'
                ])
            return response
        
        elif operation == 'send_email':
            subject = request.POST.get('email_subject')
            message = request.POST.get('email_message')
            
            if not subject or not message:
                messages.error(request, 'Please provide both subject and message.')
                return redirect('admin_tools:bulk_user_operations')
            
            # Here you would implement your email sending logic
            # For now, we'll just log it
            for user in users:
                AdminAuditLog.objects.create(
                    admin=request.user,
                    action='bulk_email',
                    entity_type='User',
                    entity_id=str(user.id),
                    details=f'Sent email to {user.email}: {subject}'
                    )
            messages.success(request, f'Email queued for {users.count()} users.')
    
    # Get all users for the selection
    users = User.objects.all().order_by('-date_joined')
    
    context = {
        'users': users,
        'page_title': 'Bulk User Operations',
        'page_description': 'Perform bulk operations on selected users.'
    }
    return render(request, 'admin_tools/bulk_operations.html', context)

# System Monitoring Views
@login_required
@user_passes_test(is_superadmin)
def system_health(request):
    # Get current system metrics
    cpu_usage = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Log system health
    SystemHealthLog.objects.create(
        cpu_usage=cpu_usage,
        memory_usage=memory.percent,
        disk_usage=disk.percent,
        database_queries=0,  # This would need to be implemented
        response_time=0,     # This would need to be implemented
        error_count=ErrorLog.objects.filter(
            timestamp__gte=timezone.now() - timedelta(hours=1)
        ).count()
    )
    
    # Get historical data
    historical_data = SystemHealthLog.objects.order_by('-timestamp')[:100]
    
    context = {
        'current_metrics': {
            'cpu_usage': cpu_usage,
            'memory_usage': memory.percent,
            'disk_usage': disk.percent,
        },
        'historical_data': historical_data,
        'page_title': 'System Health Monitor',
    }
    return render(request, 'admin_tools/system_health.html', context)

@login_required
@user_passes_test(is_superadmin)
def error_logs(request):
    logs = ErrorLog.objects.select_related('user').order_by('-timestamp')
    paginator = Paginator(logs, 50)
    page = request.GET.get('page', 1)
    logs_page = paginator.get_page(page)
    
    context = {
        'logs': logs_page,
        'page_title': 'Error Logs',
    }
    return render(request, 'admin_tools/error_logs.html', context)

@login_required
@user_passes_test(is_superadmin)
def api_monitoring(request):
    # Get API usage statistics
    api_logs = APILog.objects.all()
    
    # Calculate metrics
    total_requests = api_logs.count()
    success_rate = api_logs.filter(status_code__lt=400).count() / total_requests * 100 if total_requests > 0 else 0
    avg_response_time = api_logs.aggregate(avg=Avg('response_time'))['avg'] or 0
    
    # Get endpoint usage
    endpoint_usage = api_logs.values('endpoint').annotate(
        count=Count('id'),
        avg_time=Avg('response_time')
    ).order_by('-count')
    
    context = {
        'total_requests': total_requests,
        'success_rate': success_rate,
        'avg_response_time': avg_response_time,
        'endpoint_usage': endpoint_usage,
        'page_title': 'API Monitoring',
    }
    return render(request, 'admin_tools/api_monitoring.html', context)

# Analytics Views
@login_required
@user_passes_test(is_superadmin)
def analytics_dashboard(request):
    # Get all saved reports
    reports = AnalyticsReport.objects.all().order_by('-created_at')
    
    # Get basic metrics
    total_users = User.objects.count()
    total_enrollments = Enrollment.objects.count()
    total_revenue = Enrollment.objects.aggregate(
        total=Sum('program__price')
    )['total'] or 0
    
    context = {
        'reports': reports,
        'total_users': total_users,
        'total_enrollments': total_enrollments,
        'total_revenue': total_revenue,
        'page_title': 'Analytics Dashboard',
    }
    return render(request, 'admin_tools/analytics.html', context)

@login_required
@user_passes_test(is_superadmin)
def create_report(request):
    if request.method == 'POST':
        report_type = request.POST.get('report_type')
        date_range = request.POST.get('date_range')
        metrics = request.POST.getlist('metrics')
        
        report = AnalyticsReport.objects.create(
            report_type=report_type,
            date_range=date_range,
            metrics=json.dumps(metrics),
            created_by=request.user
        )
        
        # Generate report data
        data = generate_report_data(report)
        AnalyticsData.objects.create(
            report=report,
            data=json.dumps(data)
        )
        
        messages.success(request, 'Report created successfully.')
        return redirect('admin_tools:view_report', report_id=report.id)
    
    context = {
        'page_title': 'Create Analytics Report',
    }
    return render(request, 'admin_tools/create_report.html', context)

@login_required
@user_passes_test(is_superadmin)
def view_report(request, report_id):
    report = get_object_or_404(AnalyticsReport, id=report_id)
    data = report.data.first()
    
    if not data:
        messages.error(request, 'No data available for this report.')
        return redirect('admin_tools:analytics_dashboard')
    
    context = {
        'report': report,
        'data': json.loads(data.data),
        'page_title': f'Report: {report.report_type}',
    }
    return render(request, 'admin_tools/view_report.html', context)

def generate_report_data(report):
    """Helper function to generate report data based on type and metrics."""
    data = {}
    start_date = timezone.now() - timedelta(days=int(report.date_range))
    
    if 'user_growth' in report.metrics:
        user_data = User.objects.filter(
            date_joined__gte=start_date
        ).annotate(
            date=TruncDate('date_joined')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        data['user_growth'] = list(user_data)
    
    if 'enrollment_trends' in report.metrics:
        enrollment_data = Enrollment.objects.filter(
            created_at__gte=start_date
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id'),
            revenue=Sum('amount_paid')
        ).order_by('date')
        data['enrollment_trends'] = list(enrollment_data)
    
    return data

def calculate_growth_rate(current, previous):
    """Helper function to calculate growth rate."""
    if not previous:
        return 100
    return ((current - previous) / previous) * 100

# Admin Dashboard Views
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Get basic metrics
    total_users = User.objects.count()
    
    # Program metrics
    total_programs = EducationalProgram.objects.count()
    active_students = User.objects.filter(role='student', is_active=True).count()
    active_programs_list = EducationalProgram.objects.filter(
        status='active'
    ).select_related('instructor').prefetch_related('students').order_by('-created_at')[:5]
    
    # Calculate program metrics
    total_enrollments = sum(program.students.count() for program in EducationalProgram.objects.all())
    total_completed = LessonProgress.objects.filter(is_completed=True).count()
    total_lessons = Course.objects.count()
    
    enrollment_rate = (total_enrollments / total_users * 100) if total_users > 0 else 0
    completion_rate = (total_completed / (total_lessons * total_enrollments) * 100) if (total_lessons * total_enrollments) > 0 else 0
    
    # Calculate average rating
    avg_rating = ProgramRating.objects.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Calculate total revenue from program prices
    total_revenue = EducationalProgram.objects.aggregate(
        total=Sum('price')
    )['total'] or 0
    
    # Initialize Zoom metrics with defaults
    upcoming_classes = []
    active_meetings = 0
    
    # Try to get Zoom metrics if the app is installed
    try:
        from zoom_integration.models import VirtualClass, ZoomMeeting
        
        upcoming_classes = VirtualClass.objects.filter(
            start_time__gt=timezone.now(),
            status='scheduled'
        ).order_by('start_time')[:5]
        
        active_meetings = ZoomMeeting.objects.filter(
            start_time__lte=timezone.now(),
            start_time__gte=timezone.now() - timedelta(hours=2)
        ).count()
    except (ImportError, django.db.utils.OperationalError):
        # Zoom integration is not installed or tables don't exist
        pass
    
    # Recent activities
    recent_activities = []
    
    # Add program activities
    recent_programs = EducationalProgram.objects.order_by('-created_at')[:3]
    for program in recent_programs:
        recent_activities.append({
            'type': 'success',
            'action': 'New Program',
            'description': f'New program created: <b>{program.title}</b>',
            'timestamp': program.created_at
        })
    
    # Add enrollment activities
    recent_enrollments = User.objects.filter(
        enrolled_programs__isnull=False
    ).order_by('-date_joined')[:3]
    for student in recent_enrollments:
        recent_activities.append({
            'type': 'info',
            'action': 'New Enrollment',
            'description': f'Student <b>{student.get_full_name()}</b> enrolled in a program',
            'timestamp': student.date_joined
        })
    
    # Add Zoom activities if available
    try:
        recent_meetings = ZoomMeeting.objects.order_by('-created_at')[:3]
        for meeting in recent_meetings:
            recent_activities.append({
                'type': 'primary',
                'action': 'New Meeting',
                'description': f'New meeting scheduled: <b>{meeting.topic}</b>',
                'timestamp': meeting.created_at
            })
    except (NameError, django.db.utils.OperationalError):
        pass
    
    # Add user activities
    user_activities = UserActivityLog.objects.select_related('user').order_by('-timestamp')[:3]
    for activity in user_activities:
        recent_activities.append({
            'type': 'primary',
            'action': activity.action,
            'description': activity.description,
            'timestamp': activity.timestamp
        })
    
    # Sort activities by timestamp
    recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)

    context = {
        'total_users': total_users,
        'total_programs': total_programs,
        'active_students': active_students,
        'active_programs_list': active_programs_list,
        'upcoming_classes': upcoming_classes,
        'active_meetings': active_meetings,
        'enrollment_rate': round(enrollment_rate, 1),
        'completion_rate': round(completion_rate, 1),
        'avg_rating': round(avg_rating, 1),
        'total_revenue': total_revenue,
        'recent_activities': recent_activities[:5],  # Show only the 5 most recent activities
        'page_title': 'Admin Dashboard',
    }
    return render(request, 'admin_tools/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def user_management(request):
    """View for managing users."""
    search_query = request.GET.get('search', '')
    users = User.objects.all().order_by('-date_joined')
    
    # Debug logging
    print(f"Total users found: {users.count()}")
    print(f"Current user: {request.user.username}, is_staff: {request.user.is_staff}")
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    paginator = Paginator(users, 10)  # Show 10 users per page
    page = request.GET.get('page')
    users = paginator.get_page(page)
    
    context = {
        'users': users,
        'page_title': 'User Management',
        'page_description': 'Manage system users and their roles.'
    }
    
    # Debug logging
    print(f"Context users count: {len(users)}")
    print(f"Template being rendered: admin_tools/user_management.html")
    
    return render(request, 'admin_tools/user_management.html', context)

@login_required
@user_passes_test(is_admin)
def edit_user(request, user_id):
    """View for editing user details."""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        # Update user details
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        
        # Log the edit
        AdminAuditLog.objects.create(
            admin=request.user,
            action='edit_user',
            entity_type='User',
            entity_id=str(user.id),
            details=f'Updated user details for {user.email}'
        )
        
        messages.success(request, 'User details updated successfully.')
        return redirect('admin_tools:user_management')
    
    return redirect('admin_tools:user_management')

@login_required
@user_passes_test(is_admin)
def toggle_user_status(request, user_id):
    """View for toggling user active status."""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        user.is_active = not user.is_active
        user.save()
        
        # Log the status change
        action = 'activate_user' if user.is_active else 'deactivate_user'
        AdminAuditLog.objects.create(
            admin=request.user,
            action=action,
            entity_type='User',
            entity_id=str(user.id),
            details=f'{"Activated" if user.is_active else "Deactivated"} user {user.email}'
        )
        
        messages.success(
            request,
            f'User {user.email} has been {"activated" if user.is_active else "deactivated"}.'
        )
    return redirect('admin_tools:user_management')

@login_required
@user_passes_test(is_admin)
def update_user_role(request, user_id):
    """View for updating user role."""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        new_role = request.POST.get('role')
        ip_address = request.META.get('REMOTE_ADDR')
        
        if new_role in dict(User.ROLE_CHOICES).keys():
            old_role = user.role
            user.role = new_role
            user.save()
            
            # Log the role change
            AdminAuditLog.objects.create(
                admin=request.user,
                action='update_user_role',
                entity_type='User',
                entity_id=str(user.id),
                details=f'Changed user {user.email} role from {old_role} to {new_role}',
                ip_address=ip_address
            )
            
            messages.success(request, f'User role updated to {new_role} successfully.')
        else:
            messages.error(request, 'Invalid role selected.')
    
    return redirect('admin_tools:user_management')

@login_required
@user_passes_test(is_admin)
def admin_content_moderation(request):
    context = {
        'page_title': 'Content Moderation',
    }
    return render(request, 'admin_tools/content_moderation.html', context)

@login_required
@user_passes_test(is_admin)
def admin_settings(request):
    """View for managing system settings."""
    if request.method == 'POST':
        # Update settings
        for key, value in request.POST.items():
            if key.startswith('setting_'):
                setting_key = key.replace('setting_', '')
                AdminSetting.objects.update_or_create(
                    key=setting_key,
                    defaults={'value': value}
                )
        
        # Log the settings update
        AdminAuditLog.objects.create(
            admin=request.user,
            action='update_settings',
            entity_type='Settings',
            details='Updated system settings'
        )
        
        messages.success(request, 'System settings updated successfully.')
        return redirect('admin_tools:settings')
    
    # Get current settings
    settings = AdminSetting.objects.all()
    settings_dict = {setting.key: setting.value for setting in settings}
    
    context = {
        'settings': settings_dict,
        'page_title': 'System Settings',
        'page_description': 'Manage system-wide settings and configurations.'
    }
    return render(request, 'admin_tools/settings.html', context)

@login_required
@user_passes_test(is_admin)
def announcement_categories(request):
    """View for managing announcement categories."""
    if request.method == 'POST':
        action = request.POST.get('action')
        category_id = request.POST.get('category_id')
        
        if action == 'create':
            name = request.POST.get('name')
            description = request.POST.get('description')
            is_active = request.POST.get('is_active') == 'on'
            
            AnnouncementCategory.objects.create(
                name=name,
                description=description,
                is_active=is_active
            )
            messages.success(request, 'Category created successfully.')
            
        elif action == 'edit' and category_id:
            category = get_object_or_404(AnnouncementCategory, id=category_id)
            category.name = request.POST.get('name')
            category.description = request.POST.get('description')
            category.is_active = request.POST.get('is_active') == 'on'
            category.save()
            messages.success(request, 'Category updated successfully.')
            
        elif action == 'delete' and category_id:
            category = get_object_or_404(AnnouncementCategory, id=category_id)
            category.delete()
            messages.success(request, 'Category deleted successfully.')
    
    categories = AnnouncementCategory.objects.all().order_by('name')
    context = {
        'categories': categories,
        'page_title': 'Announcement Categories',
        'page_description': 'Manage announcement categories.'
    }
    return render(request, 'admin_tools/announcement_categories.html', context)

@login_required
@user_passes_test(is_admin)
def announcement_settings(request):
    """View for managing announcement settings."""
    if request.method == 'POST':
        # Update announcement settings
        settings = {
            'announcement_display_duration': request.POST.get('display_duration'),
            'announcement_auto_archive': request.POST.get('auto_archive') == 'on',
            'announcement_notification': request.POST.get('notification') == 'on',
            'announcement_max_display': request.POST.get('max_display'),
            'announcement_approval_required': request.POST.get('approval_required') == 'on'
        }
        
        for key, value in settings.items():
            AdminSetting.objects.update_or_create(
                key=key,
                defaults={'value': value}
            )
        
        messages.success(request, 'Announcement settings updated successfully.')
    
    # Get current settings
    settings = AdminSetting.objects.filter(key__startswith='announcement_')
    settings_dict = {setting.key: setting.value for setting in settings}
    
    context = {
        'settings': settings_dict,
        'page_title': 'Announcement Settings',
        'page_description': 'Configure announcement system settings.'
    }
    return render(request, 'admin_tools/announcement_settings.html', context)

@login_required
@user_passes_test(is_admin)
def announcement_list(request):
    """Public view for listing announcements."""
    announcements = Announcement.objects.select_related(
        'category', 'created_by'
    ).filter(
        is_active=True,
        start_date__lte=timezone.now()
    ).filter(
        Q(end_date__gte=timezone.now()) | Q(end_date__isnull=True)
    ).order_by('-priority', '-created_at')
    
    # Filtering
    category = request.GET.get('category')
    search = request.GET.get('search')
    
    if category:
        announcements = announcements.filter(category__name=category)
    if search:
        announcements = announcements.filter(
            Q(title__icontains=search) | 
            Q(content__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(announcements, 10)
    page = request.GET.get('page', 1)
    announcements_page = paginator.get_page(page)
    
    categories = AnnouncementCategory.objects.filter(is_active=True)
    
    context = {
        'announcements': announcements_page,
        'categories': categories,
        'page_title': 'Announcements',
        'page_description': 'Latest announcements and updates.'
    }
    return render(request, 'admin_tools/announcement_list.html', context)

@login_required
@user_passes_test(is_admin)
def create_announcement(request):
    """View for creating new announcements."""
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        priority = request.POST.get('priority')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        is_active = request.POST.get('is_active') == 'on'
        
        category = get_object_or_404(AnnouncementCategory, id=category_id)
        
        announcement = Announcement.objects.create(
            title=title,
            content=content,
            category=category,
            priority=priority,
            start_date=start_date,
            end_date=end_date,
            is_active=is_active,
            created_by=request.user
        )
        
        messages.success(request, f'Announcement "{announcement.title}" created successfully.')
        return redirect('admin_tools:announcement_list')
    
    categories = AnnouncementCategory.objects.filter(is_active=True)
    context = {
        'categories': categories,
        'page_title': 'Create Announcement',
        'page_description': 'Create a new system announcement.'
    }
    return render(request, 'admin_tools/create_announcement.html', context)

@login_required
@user_passes_test(is_admin)
def edit_announcement(request, announcement_id):
    """View for editing existing announcements."""
    announcement = get_object_or_404(Announcement, id=announcement_id)
    
    if request.method == 'POST':
        announcement.title = request.POST.get('title')
        announcement.content = request.POST.get('content')
        announcement.category_id = request.POST.get('category')
        announcement.priority = request.POST.get('priority')
        announcement.start_date = request.POST.get('start_date')
        announcement.end_date = request.POST.get('end_date')
        announcement.is_active = request.POST.get('is_active') == 'on'
        announcement.save()
        
        messages.success(request, f'Announcement "{announcement.title}" updated successfully.')
        return redirect('admin_tools:announcement_list')
    
    categories = AnnouncementCategory.objects.filter(is_active=True)
    context = {
        'announcement': announcement,
        'categories': categories,
        'page_title': 'Edit Announcement',
        'page_description': 'Edit existing announcement.'
    }
    return render(request, 'admin_tools/edit_announcement.html', context)

@login_required
@user_passes_test(is_admin)
def delete_announcement(request, announcement_id):
    """View for deleting announcements."""
    announcement = get_object_or_404(Announcement, id=announcement_id)
    title = announcement.title
    announcement.delete()
    
    messages.success(request, f'Announcement "{title}" deleted successfully.')
    return redirect('admin_tools:announcement_list')

@login_required
@user_passes_test(is_admin)
def admin_faqs(request):
    """View for managing FAQs in the admin panel."""
    if request.method == 'POST':
        action = request.POST.get('action')
        faq_id = request.POST.get('faq_id')
        
        if action == 'create':
            question = request.POST.get('question')
            answer = request.POST.get('answer')
            category = request.POST.get('category')
            order = request.POST.get('order')
            is_active = request.POST.get('is_active') == 'on'
            
            FAQ.objects.create(
                question=question,
                answer=answer,
                category=category,
                order=order,
                is_active=is_active
            )
            messages.success(request, 'FAQ created successfully.')
            
        elif action == 'edit' and faq_id:
            faq = get_object_or_404(FAQ, id=faq_id)
            faq.question = request.POST.get('question')
            faq.answer = request.POST.get('answer')
            faq.category = request.POST.get('category')
            faq.order = request.POST.get('order')
            faq.is_active = request.POST.get('is_active') == 'on'
            faq.save()
            messages.success(request, 'FAQ updated successfully.')
            
        elif action == 'delete' and faq_id:
            faq = get_object_or_404(FAQ, id=faq_id)
            faq.delete()
            messages.success(request, 'FAQ deleted successfully.')
    
    # Get all FAQs grouped by category
    faqs_by_category = {}
    for faq in FAQ.objects.all().order_by('category', 'order'):
        if faq.category not in faqs_by_category:
            faqs_by_category[faq.category] = []
        faqs_by_category[faq.category].append(faq)
    
    context = {
        'faqs_by_category': faqs_by_category,
        'page_title': 'Manage FAQs',
        'page_description': 'Create, edit, and manage frequently asked questions.'
    }
    return render(request, 'admin_tools/faqs.html', context)

@login_required
@user_passes_test(is_admin)
def faq_management(request):
    """Placeholder view for FAQ Management."""
    return render(request, 'admin_tools/faq_management.html', {})

@login_required
@user_passes_test(is_admin)
def add_role(request):
    """Placeholder view for adding a role."""
    return render(request, 'admin_tools/add_role.html', {})

@login_required
@user_passes_test(is_admin)
def audit_logs(request):
    """View for displaying admin audit logs."""
    logs = AdminAuditLog.objects.select_related('admin').order_by('-timestamp')
    paginator = Paginator(logs, 25)
    page = request.GET.get('page', 1)
    logs_page = paginator.get_page(page)
    context = {
        'logs': logs_page,
        'page_title': 'Audit Logs',
    }
    return render(request, 'admin_tools/audit_logs.html', context)

def public_announcements(request):
    """Public view for displaying announcements."""
    announcements = Announcement.objects.select_related(
        'category', 'created_by'
    ).filter(
        is_active=True,
        start_date__lte=timezone.now()
    ).filter(
        Q(end_date__gte=timezone.now()) | Q(end_date__isnull=True)
    ).order_by('-priority', '-created_at')
    
    # Filtering
    category = request.GET.get('category')
    search = request.GET.get('search')
    
    if category:
        announcements = announcements.filter(category__name=category)
    if search:
        announcements = announcements.filter(
            Q(title__icontains=search) | 
            Q(content__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(announcements, 10)
    page = request.GET.get('page', 1)
    announcements_page = paginator.get_page(page)
    
    categories = AnnouncementCategory.objects.filter(is_active=True)
    
    context = {
        'announcements': announcements_page,
        'categories': categories,
        'page_title': 'Announcements',
        'page_description': 'Latest announcements and updates.'
    }
    return render(request, 'admin_tools/public_announcements.html', context)

@login_required
@user_passes_test(is_admin)
def admin_approve_user(request, user_id):
    """View for approving a user's registration."""
    user = get_object_or_404(User, id=user_id)
    extra_info = None
    if user.role == 'teacher':
        profile = getattr(user, 'profile', None)
        if profile:
            extra_info = {
                'education': profile.education,
                'experience': profile.experience,
                'expertise': profile.expertise,
                'cv': profile.cv.url if profile.cv else None,
            }
    elif user.role == 'student':
        student_profile = getattr(user, 'studentprofile', None)
        if student_profile:
            extra_info = {
                'age': student_profile.age,
                'interests': student_profile.interests,
            }
    
    if request.method == 'POST':
        user.is_active = True
        user.is_approved = True
        user.save()
        # Log the approval
        AdminAuditLog.objects.create(
            admin=request.user,
            action='approve_user',
            entity_type='User',
            entity_id=str(user.id),
            details=f'Approved user registration for {user.email}'
        )
        messages.success(request, f'User {user.email} has been approved.')
        return redirect('admin_tools:user_management')
    
    context = {
        'user': user,
        'extra_info': extra_info,
        'page_title': 'Approve User',
        'page_description': 'Approve user registration request.'
    }
    return render(request, 'admin_tools/approve_user.html', context)

@login_required
@user_passes_test(is_admin)
def admin_reject_user(request, user_id):
    """View for rejecting a user's registration."""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        # Log the rejection before deleting
        AdminAuditLog.objects.create(
            admin=request.user,
            action='reject_user',
            entity_type='User',
            entity_id=str(user.id),
            details=f'Rejected user registration for {user.email}'
        )
        
        user.delete()
        messages.success(request, f'User registration for {user.email} has been rejected.')
        return redirect('admin_tools:user_management')
    
    context = {
        'user': user,
        'page_title': 'Reject User',
        'page_description': 'Reject user registration request.'
    }
    return render(request, 'admin_tools/reject_user.html', context)

@login_required
@user_passes_test(is_admin)
def admin_create_user(request):
    """View for creating a new user."""
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Log the user creation
            AdminAuditLog.objects.create(
                admin=request.user,
                action='create_user',
                entity_type='User',
                entity_id=str(user.id),
                details=f'Created new user: {user.email}'
            )
            
            messages.success(request, f'User {user.email} has been created successfully.')
            return redirect('admin_tools:user_management')
    else:
        form = AdminUserCreationForm()
    
    context = {
        'form': form,
        'page_title': 'Create User',
        'page_description': 'Create a new user account.'
    }
    return render(request, 'admin_tools/create_user.html', context)

@login_required
@user_passes_test(is_superadmin)
def add_group(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        permission_ids = request.POST.getlist('permissions')
        if name:
            group, created = Group.objects.get_or_create(name=name)
            if permission_ids:
                perms = Permission.objects.filter(id__in=permission_ids)
                group.permissions.set(perms)
            group.save()
            messages.success(request, f'Group "{name}" created successfully.')
            return redirect('admin_tools:user_permissions')
        else:
            messages.error(request, 'Group name is required.')
            return redirect('admin_tools:user_permissions')
    # For GET, redirect to permissions page
    return redirect('admin_tools:user_permissions')
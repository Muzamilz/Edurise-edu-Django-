from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from datetime import timedelta, datetime
from .models import (
    ZoomUser, ZoomMeeting, ZoomAttendance, ZoomAnalytics,
    MeetingTemplate, BulkMeetingSchedule, Resource, MeetingFeedback, VirtualClass
)
from programs.models import EducationalProgram
from enrollments.models import Enrollment
from .zoom_client import ZoomClient
from django.http import JsonResponse
from django.db.models import Count, Avg, Sum
import json
from authentication.models import User

# Create your views here.

@login_required
@user_passes_test(lambda u: u.role == 'teacher')
def connect_zoom(request):
    """Connect a teacher's Zoom account."""
    if request.method == 'POST':
        # Handle Zoom OAuth connection
        zoom_client = ZoomClient()
        auth_url = zoom_client.get_authorization_url()
        return redirect(auth_url)
    return render(request, 'zoom_integration/connect.html')

@login_required
def zoom_callback(request):
    code = request.GET.get('code')
    if code:
        zoom_client = ZoomClient()
        tokens = zoom_client.get_access_token(code)
        
        ZoomUser.objects.update_or_create(
            user=request.user,
            defaults={
                'zoom_user_id': tokens['user_id'],
                'access_token': tokens['access_token'],
                'refresh_token': tokens['refresh_token'],
                'token_expires_at': timezone.now() + timedelta(seconds=tokens['expires_in'])
            }
        )
        messages.success(request, 'Successfully connected to Zoom!')
    return redirect('teacher_dashboard')

@login_required
@user_passes_test(lambda u: u.role == 'teacher')
def create_meeting(request):
    """Create a new Zoom meeting."""
    if not request.user.is_teacher:
        messages.error(request, 'Only teachers can create meetings.')
        return redirect('home')
    
    if request.method == 'POST':
        program_id = request.POST.get('program')
        topic = request.POST.get('topic')
        start_time = request.POST.get('start_time')
        duration = request.POST.get('duration')
        is_recurring = request.POST.get('is_recurring') == 'on'
        recurrence_pattern = request.POST.get('recurrence_pattern')
        
        program = get_object_or_404(EducationalProgram, id=program_id)
        zoom_user = get_object_or_404(ZoomUser, user=request.user)
        
        zoom_client = ZoomClient(zoom_user.access_token)
        meeting_data = zoom_client.create_meeting(
            topic=topic,
            start_time=start_time,
            duration=duration,
            is_recurring=is_recurring,
            recurrence_pattern=json.loads(recurrence_pattern) if recurrence_pattern else None
        )
        
        meeting = ZoomMeeting.objects.create(
            teacher=request.user,
            program=program,
            topic=topic,
            start_time=start_time,
            duration=duration,
            zoom_meeting_id=meeting_data['id'],
            join_url=meeting_data['join_url'],
            is_recurring=is_recurring,
            recurrence_pattern=json.loads(recurrence_pattern) if recurrence_pattern else None
        )
        
        messages.success(request, 'Meeting created successfully!')
        return redirect('meeting_list')
    
    assigned_programs = EducationalProgram.objects.filter(teachers=request.user)
    return render(request, 'zoom_integration/create_meeting.html', {
        'assigned_programs': assigned_programs
    })

@login_required
def meeting_list(request):
    """List all Zoom meetings for a teacher."""
    if request.user.role == 'teacher':
        meetings = ZoomMeeting.objects.filter(teacher=request.user)
    elif request.user.role == 'student':
        meetings = ZoomMeeting.objects.filter(program__enrollments__student=request.user)
    else:
        meetings = ZoomMeeting.objects.all()
    
    return render(request, 'zoom_integration/meeting_list.html', {
        'meetings': meetings
    })

@login_required
def meeting_detail(request, meeting_id):
    meeting = get_object_or_404(ZoomMeeting, id=meeting_id)
    attendance = ZoomAttendance.objects.filter(meeting=meeting)
    
    return render(request, 'zoom_integration/meeting_detail.html', {
        'meeting': meeting,
        'attendance': attendance
    })

@login_required
def upcoming_meetings(request):
    """Show upcoming meetings for students."""
    if request.user.is_student:
        meetings = ZoomMeeting.objects.filter(
            program__enrollments__student=request.user,
            start_time__gt=timezone.now()
        ).order_by('start_time')
    else:
        meetings = ZoomMeeting.objects.filter(
            start_time__gt=timezone.now()
        ).order_by('start_time')
    
    return render(request, 'zoom_integration/upcoming_meetings.html', {
        'meetings': meetings
    })

@login_required
def track_attendance(request, meeting_id):
    if not request.user.is_teacher:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    meeting = get_object_or_404(ZoomMeeting, id=meeting_id)
    zoom_user = get_object_or_404(ZoomUser, user=request.user)
    
    zoom_client = ZoomClient(zoom_user.access_token)
    participants = zoom_client.get_meeting_participants(meeting.zoom_meeting_id)
    
    for participant in participants:
        student = get_object_or_404(settings.AUTH_USER_MODEL, email=participant['user_email'])
        ZoomAttendance.objects.update_or_create(
            meeting=meeting,
            student=student,
            defaults={
                'join_time': participant['join_time'],
                'leave_time': participant.get('leave_time'),
                'duration': participant.get('duration'),
                'status': 'present' if participant.get('duration', 0) > 30 else 'late'
            }
        )
    
    return JsonResponse({'status': 'success'})

@login_required
def program_analytics(request, program_id):
    if not request.user.is_admin:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    program = get_object_or_404(EducationalProgram, id=program_id)
    analytics = ZoomAnalytics.objects.filter(program=program).order_by('-date')[:30]
    
    return render(request, 'zoom_integration/program_analytics.html', {
        'program': program,
        'analytics': analytics
    })

@login_required
def update_analytics(request):
    if not request.user.is_admin:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    programs = EducationalProgram.objects.all()
    today = timezone.now().date()
    
    for program in programs:
        meetings = ZoomMeeting.objects.filter(
            program=program,
            start_time__date=today
        )
        
        total_meetings = meetings.count()
        total_participants = ZoomAttendance.objects.filter(
            meeting__in=meetings
        ).count()
        
        if total_meetings > 0:
            average_duration = meetings.aggregate(
                avg_duration=Avg('duration')
            )['avg_duration']
        else:
            average_duration = 0
        
        ZoomAnalytics.objects.update_or_create(
            program=program,
            date=today,
            defaults={
                'total_meetings': total_meetings,
                'total_participants': total_participants,
                'average_duration': average_duration,
                'total_attendance': total_participants
            }
        )
    
    return JsonResponse({'status': 'success'})

@login_required
@user_passes_test(lambda u: u.role == 'teacher')
def create_meeting_template(request):
    if request.method == 'POST':
        program_id = request.POST.get('program')
        name = request.POST.get('name')
        topic = request.POST.get('topic')
        duration = request.POST.get('duration')
        settings = json.loads(request.POST.get('settings', '{}'))
        
        program = get_object_or_404(EducationalProgram, id=program_id)
        
        template = MeetingTemplate.objects.create(
            teacher=request.user,
            program=program,
            name=name,
            topic=topic,
            duration=duration,
            settings=settings
        )
        
        messages.success(request, 'Meeting template created successfully!')
        return redirect('zoom:template_list')
    
    assigned_programs = EducationalProgram.objects.filter(teachers=request.user)
    return render(request, 'zoom_integration/create_template.html', {
        'assigned_programs': assigned_programs
    })

@login_required
@user_passes_test(lambda u: u.role == 'teacher')
def template_list(request):
    templates = MeetingTemplate.objects.filter(teacher=request.user)
    return render(request, 'zoom_integration/template_list.html', {
        'templates': templates
    })

@login_required
@user_passes_test(lambda u: u.role == 'teacher')
def create_bulk_schedule(request):
    if request.method == 'POST':
        program_id = request.POST.get('program')
        template_id = request.POST.get('template')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        days_of_week = json.loads(request.POST.get('days_of_week', '[]'))
        time_slots = json.loads(request.POST.get('time_slots', '[]'))
        
        program = get_object_or_404(EducationalProgram, id=program_id)
        template = get_object_or_404(MeetingTemplate, id=template_id)
        
        schedule = BulkMeetingSchedule.objects.create(
            teacher=request.user,
            program=program,
            template=template,
            start_date=start_date,
            end_date=end_date,
            days_of_week=days_of_week,
            time_slots=time_slots
        )
        
        # Create meetings based on the schedule
        create_meetings_from_schedule(schedule)
        
        messages.success(request, 'Bulk schedule created successfully!')
        return redirect('zoom:bulk_schedule_list')
    
    assigned_programs = EducationalProgram.objects.filter(teachers=request.user)
    templates = MeetingTemplate.objects.filter(teacher=request.user)
    return render(request, 'zoom_integration/create_bulk_schedule.html', {
        'assigned_programs': assigned_programs,
        'templates': templates
    })

def create_meetings_from_schedule(schedule):
    """Create Zoom meetings based on a bulk schedule."""
    zoom_user = get_object_or_404(ZoomUser, user=schedule.teacher)
    zoom_client = ZoomClient(zoom_user.access_token)
    
    current_date = schedule.start_date
    while current_date <= schedule.end_date:
        if current_date.weekday() in schedule.days_of_week:
            for time_slot in schedule.time_slots:
                start_time = datetime.combine(current_date, datetime.strptime(time_slot, '%H:%M').time())
                
                # Create meeting in Zoom
                meeting_data = zoom_client.create_meeting(
                    topic=schedule.template.topic,
                    start_time=start_time.isoformat(),
                    duration=schedule.template.duration,
                    settings=schedule.template.settings
                )
                
                # Create meeting in database
                meeting = ZoomMeeting.objects.create(
                    teacher=schedule.teacher,
                    program=schedule.program,
                    topic=schedule.template.topic,
                    start_time=start_time,
                    duration=schedule.template.duration,
                    zoom_meeting_id=meeting_data['id'],
                    join_url=meeting_data['join_url'],
                    template=schedule.template
                )
                
                schedule.created_meetings.add(meeting)
        
        current_date += timedelta(days=1)
    
    schedule.status = 'completed'
    schedule.save()

@login_required
@user_passes_test(lambda u: u.role == 'teacher')
def bulk_schedule_list(request):
    schedules = BulkMeetingSchedule.objects.filter(teacher=request.user)
    return render(request, 'zoom_integration/bulk_schedule_list.html', {
        'schedules': schedules
    })

@login_required
def submit_meeting_feedback(request, meeting_id):
    if request.method == 'POST':
        meeting = get_object_or_404(ZoomMeeting, id=meeting_id)
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        feedback = MeetingFeedback.objects.create(
            meeting=meeting,
            student=request.user,
            rating=rating,
            comment=comment
        )
        
        return JsonResponse({
            'status': 'success',
            'feedback': {
                'rating': feedback.rating,
                'comment': feedback.comment,
                'created_at': feedback.created_at.isoformat()
            }
        })
    
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def upload_meeting_resource(request, meeting_id):
    if request.method == 'POST':
        meeting = get_object_or_404(ZoomMeeting, id=meeting_id)
        name = request.POST.get('name')
        description = request.POST.get('description')
        category = request.POST.get('category')
        file = request.FILES.get('file')
        
        resource = Resource.objects.create(
            meeting=meeting,
            name=name,
            description=description,
            category=category,
            file=file,
            uploaded_by=request.user
        )
        
        return JsonResponse({
            'status': 'success',
            'resource': {
                'id': resource.id,
                'name': resource.name,
                'url': resource.file.url
            }
        })
    
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def get_meeting_analytics(request, meeting_id):
    meeting = get_object_or_404(ZoomMeeting, id=meeting_id)
    
    attendance_stats = meeting.get_attendance_stats()
    feedback_stats = meeting.get_feedback_stats()
    
    return JsonResponse({
        'attendance': attendance_stats,
        'feedback': feedback_stats
    })

def is_admin(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(is_admin)
def virtual_class_list(request):
    classes = VirtualClass.objects.all().order_by('-created_at')
    context = {
        'classes': classes,
        'page_title': 'Virtual Classes',
    }
    return render(request, 'zoom_integration/virtual_classes.html', context)

@login_required
@user_passes_test(is_admin)
def create_virtual_class(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        program_id = request.POST.get('program')
        instructor_id = request.POST.get('instructor')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        meeting_link = request.POST.get('meeting_link')
        status = request.POST.get('status', 'scheduled')

        program = get_object_or_404(EducationalProgram, id=program_id)
        instructor = get_object_or_404(User, id=instructor_id, role='teacher')

        virtual_class = VirtualClass.objects.create(
            title=title,
            description=description,
            program=program,
            instructor=instructor,
            start_time=start_time,
            end_time=end_time,
            meeting_link=meeting_link,
            status=status
        )
        messages.success(request, f'Virtual class "{virtual_class.title}" created successfully.')
        return redirect('zoom_integration:virtual_class_list')

    programs = EducationalProgram.objects.filter(status='active')
    instructors = User.objects.filter(role='teacher', is_active=True)
    context = {
        'programs': programs,
        'instructors': instructors,
        'page_title': 'Create Virtual Class',
    }
    return render(request, 'zoom_integration/create_virtual_class.html', context)

@login_required
@user_passes_test(is_admin)
def edit_virtual_class(request, class_id):
    virtual_class = get_object_or_404(VirtualClass, id=class_id)
    if request.method == 'POST':
        virtual_class.title = request.POST.get('title')
        virtual_class.description = request.POST.get('description')
        virtual_class.program_id = request.POST.get('program')
        virtual_class.instructor_id = request.POST.get('instructor')
        virtual_class.start_time = request.POST.get('start_time')
        virtual_class.end_time = request.POST.get('end_time')
        virtual_class.meeting_link = request.POST.get('meeting_link')
        virtual_class.status = request.POST.get('status', 'scheduled')
        virtual_class.save()
        messages.success(request, f'Virtual class "{virtual_class.title}" updated successfully.')
        return redirect('zoom_integration:virtual_class_list')
    programs = EducationalProgram.objects.filter(status='active')
    instructors = User.objects.filter(role='teacher', is_active=True)
    context = {
        'virtual_class': virtual_class,
        'programs': programs,
        'instructors': instructors,
        'page_title': 'Edit Virtual Class',
    }
    return render(request, 'zoom_integration/edit_virtual_class.html', context)

@login_required
@user_passes_test(is_admin)
def delete_virtual_class(request, class_id):
    virtual_class = get_object_or_404(VirtualClass, id=class_id)
    if request.method == 'POST':
        virtual_class.delete()
        messages.success(request, f'Virtual class "{virtual_class.title}" deleted successfully.')
        return redirect('zoom_integration:virtual_class_list')
    context = {
        'virtual_class': virtual_class,
        'page_title': 'Delete Virtual Class',
    }
    return render(request, 'zoom_integration/delete_virtual_class.html', context)

# Add the following views from admin_tools/views.py:
# - virtual_class_list (list all virtual classes)
# - create_virtual_class
# - edit_virtual_class
# - delete_virtual_class

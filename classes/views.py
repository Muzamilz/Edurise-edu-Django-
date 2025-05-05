from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Class, ClassAttendance, ClassFeedback
from .forms import ClassForm, AttendanceForm, FeedbackForm
from .utils import create_zoom_meeting
from django.urls import reverse

@login_required
def create_class(request):
    if request.method == 'POST':
        form = ClassForm(request.POST)
        if form.is_valid():
            class_instance = form.save(commit=False)
            class_instance.teacher = request.user
            
            # Create Zoom meeting
            zoom_data = create_zoom_meeting(
                title=class_instance.title,
                start_time=class_instance.start_time,
                duration=(class_instance.end_time - class_instance.start_time).seconds // 60
            )
            
            class_instance.zoom_meeting_id = zoom_data['id']
            class_instance.zoom_join_url = zoom_data['join_url']
            class_instance.save()
            
            messages.success(request, 'Class created successfully!')
            return redirect('class_detail', class_id=class_instance.id)
    else:
        form = ClassForm()
    
    return render(request, 'classes/create_class.html', {'form': form})

@login_required
def class_detail(request, class_id):
    class_instance = get_object_or_404(Class, id=class_id)
    attendance = ClassAttendance.objects.filter(class_instance=class_instance)
    feedback = ClassFeedback.objects.filter(class_instance=class_instance)
    
    # Check if user has submitted feedback
    user_feedback = None
    if request.user.role == 'student':
        user_feedback = ClassFeedback.objects.filter(
            class_instance=class_instance,
            student=request.user
        ).first()
    
    context = {
        'class': class_instance,
        'attendance': attendance,
        'feedback': feedback,
        'user_feedback': user_feedback,
    }
    return render(request, 'classes/class_detail.html', context)

@login_required
def track_attendance(request, class_id):
    class_instance = get_object_or_404(Class, id=class_id)
    
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.class_instance = class_instance
            attendance.student = request.user
            attendance.join_time = timezone.now()
            attendance.save()
            
            messages.success(request, 'Attendance recorded successfully!')
            return redirect('class_detail', class_id=class_id)
    else:
        form = AttendanceForm()
    
    return render(request, 'classes/track_attendance.html', {'form': form, 'class': class_instance})

@login_required
def submit_feedback(request, class_id):
    class_instance = get_object_or_404(Class, id=class_id)
    
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.class_instance = class_instance
            feedback.student = request.user
            feedback.save()
            
            messages.success(request, 'Feedback submitted successfully!')
            return redirect('class_detail', class_id=class_id)
    else:
        form = FeedbackForm()
    
    return render(request, 'classes/submit_feedback.html', {'form': form, 'class': class_instance})

@login_required
def class_list(request):
    if request.user.role == 'teacher':
        classes = Class.objects.filter(teacher=request.user)
    else:
        classes = Class.objects.filter(program__enrollments__student=request.user)
    
    return render(request, 'classes/class_list.html', {'classes': classes})

@login_required
def calendar_view(request):
    """Display a calendar view of classes."""
    if request.user.role == 'teacher':
        classes = Class.objects.filter(teacher=request.user)
    else:
        classes = Class.objects.filter(program__enrollments__student=request.user)
    
    # Format classes for calendar
    calendar_events = []
    for class_instance in classes:
        calendar_events.append({
            'title': class_instance.title,
            'start': class_instance.start_time.isoformat(),
            'end': class_instance.end_time.isoformat(),
            'url': reverse('classes:class_detail', args=[class_instance.id]),
            'className': 'bg-primary' if class_instance.teacher == request.user else 'bg-success'
        })
    
    context = {
        'calendar_events': calendar_events,
    }
    return render(request, 'classes/calendar.html', context) 
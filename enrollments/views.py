from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from .models import Enrollment, ProgramProgress, CourseEnrollment, CourseProgress
from .forms import EnrollmentForm
from programs.models import EducationalProgram, ProgramModule, ProgramLesson, Course, ProgramRating
from authentication.models import User, AdminAuditLog
from classes.models import Class
from django.utils import timezone
from django.db.models import Count, Q, Avg
from django.urls import reverse
from datetime import datetime, timedelta
from .decorators import teacher_required

@login_required
def program_list(request):
    """Display a list of all available programs."""
    if request.user.role == 'teacher':
        programs = EducationalProgram.objects.filter(instructor=request.user)
    else:
        programs = EducationalProgram.objects.filter(status='published')
    return render(request, 'enrollments/program_list.html', {'programs': programs})

@login_required
def program_detail(request, program_id):
    """Display details of a specific program and its courses."""
    program = get_object_or_404(EducationalProgram, id=program_id)
    modules = program.modules.all().prefetch_related('lessons')
    courses = program.courses.all()
    context = {
        'program': program,
        'modules': modules,
        'courses': courses
    }
    return render(request, 'enrollments/program_detail.html', context)

@login_required
def course_detail(request, course_id):
    """Display course details and handle enrollment."""
    course = get_object_or_404(Course, id=course_id)
    
    if request.method == 'POST':
        if not Enrollment.objects.filter(student=request.user, program=course.program).exists():
            enrollment = Enrollment.objects.create(
                student=request.user,
                program=course.program
            )
            course_enrollment = CourseEnrollment.objects.create(
                enrollment=enrollment,
                course=course
            )
            
            # Log the enrollment request
            AdminAuditLog.objects.create(
                admin=request.user,
                action='enrollment_request',
                entity_type='course',
                entity_id=str(course.id),
                details=f'Enrollment request for course: {course.title}'
            )
            
            messages.success(request, 'Your enrollment request has been submitted.')
            return redirect('enrollments:course_detail', course_id=course.id)
        else:
            messages.info(request, 'You are already enrolled in this course.')
            return redirect('enrollments:course_detail', course_id=course.id)
    
    context = {
        'course': course,
    }
    return render(request, 'enrollments/course_detail.html', context)

@login_required
def enroll(request, program_id):
    """Enroll a student in a program."""
    program = get_object_or_404(EducationalProgram, id=program_id)
    
    if program.status != 'published':
        messages.error(request, 'This program is not available for enrollment.')
        return redirect('enrollments:program_detail', program_id=program.id)
    
    if Enrollment.objects.filter(student=request.user, program=program).exists():
        messages.warning(request, 'You are already enrolled in this program.')
        return redirect('enrollments:program_detail', program_id=program.id)
    
    if request.method == 'POST':
        form = EnrollmentForm(request.POST, request.FILES)
        if form.is_valid():
            enrollment = form.save(commit=False)
            enrollment.student = request.user
            enrollment.program = program
            enrollment.status = 'pending'
            enrollment.save()
            
            # Log the enrollment request
            AdminAuditLog.objects.create(
                admin=request.user,
                target_user=request.user,
                action='enrollment_request',
                entity_type='program',
                entity_id=str(program.id),
                details=f'Enrollment request for program: {program.title}'
            )
            
            messages.success(request, 'Enrollment request submitted successfully.')
            return redirect('enrollments:program_detail', program_id=program.id)
    else:
        form = EnrollmentForm()
    
    return render(request, 'enrollments/enroll.html', {
        'form': form,
        'program': program
    })

@login_required
def my_enrollments(request):
    """Display a list of the user's enrollments."""
    enrollments = request.user.student_enrollments.all().select_related('program')
    course_enrollments = CourseEnrollment.objects.filter(enrollment__student=request.user).select_related('course')
    
    context = {
        'enrollments': enrollments,
        'course_enrollments': course_enrollments
    }
    return render(request, 'enrollments/my_enrollments.html', context)

@login_required
def program_progress(request, enrollment_id):
    """Display a student's progress in a program."""
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, student=request.user)
    progress = ProgramProgress.objects.filter(enrollment=enrollment)
    
    return render(request, 'enrollments/program_progress.html', {
        'enrollment': enrollment,
        'progress': progress
    })

@login_required
def enrollment_detail(request, enrollment_id):
    """Display detailed information about a specific enrollment."""
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    
    # Check if user has permission to view this enrollment
    if not (request.user.role == 'admin' or 
            request.user.role == 'teacher' and enrollment.program.instructor == request.user or
            request.user == enrollment.student):
        messages.error(request, "You don't have permission to view this enrollment.")
        return redirect('enrollments:my_enrollments')
    
    # Get related data
    course_enrollments = CourseEnrollment.objects.filter(enrollment=enrollment)
    program_progress = ProgramProgress.objects.filter(enrollment=enrollment).first()
    
    context = {
        'enrollment': enrollment,
        'course_enrollments': course_enrollments,
        'program_progress': program_progress,
    }
    
    return render(request, 'enrollments/enrollment_detail.html', context)

@login_required
def course_progress(request, course_enrollment_id):
    """Display a student's progress in a course."""
    course_enrollment = get_object_or_404(CourseEnrollment, id=course_enrollment_id, enrollment__student=request.user)
    progress = CourseProgress.objects.filter(course_enrollment=course_enrollment)
    
    return render(request, 'enrollments/course_progress.html', {
        'course_enrollment': course_enrollment,
        'progress': progress
    })

@login_required
def update_progress(request, progress_id, status):
    """Update a student's progress in a course."""
    progress = get_object_or_404(CourseProgress, id=progress_id, course_enrollment__enrollment__student=request.user)
    
    if status in dict(CourseProgress.STATUS_CHOICES):
        progress.status = status
        progress.save()
        messages.success(request, 'Progress updated successfully.')
    else:
        messages.error(request, 'Invalid status.')
    
    return redirect('enrollments:course_progress', course_enrollment_id=progress.course_enrollment.id)

@login_required
@teacher_required
def teacher_dashboard(request):
    teacher = request.user
    today = timezone.now().date()
    
    # Quick Stats
    total_students = Enrollment.objects.filter(
        program__instructor=teacher,
        status='approved'
    ).values('student').distinct().count()
    
    active_programs = EducationalProgram.objects.filter(
        instructor=teacher,
        status='active'
    ).count()
    
    total_courses = Course.objects.filter(
        program__instructor=teacher
    ).count()
    
    # Calculate average rating
    ratings = ProgramRating.objects.filter(program__instructor=teacher)
    average_rating = ratings.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
    
    # User Growth (last 30 days)
    thirty_days_ago = today - timedelta(days=30)
    user_growth = []
    for i in range(30):
        date = thirty_days_ago + timedelta(days=i)
        count = Enrollment.objects.filter(
            program__instructor=teacher,
            enrollment_date__date=date
        ).count()
        user_growth.append({
            'date': date,
            'count': count
        })
    
    # Program Distribution
    programs = EducationalProgram.objects.filter(instructor=teacher)
    program_distribution = []
    for program in programs:
        program_distribution.append({
            'name': program.title,
            'count': program.enrollments.count()
        })
    
    # Performance Metrics
    total_enrollments = Enrollment.objects.filter(program__instructor=teacher).count()
    completed_enrollments = Enrollment.objects.filter(
        program__instructor=teacher,
        status='completed'
    ).count()
    
    enrollment_rate = (total_enrollments / total_courses * 100) if total_courses > 0 else 0
    completion_rate = (completed_enrollments / total_enrollments * 100) if total_enrollments > 0 else 0
    
    # Recent Activity
    recent_activity = []
    enrollments = Enrollment.objects.filter(
        program__instructor=teacher
    ).order_by('-enrollment_date')[:10]
    
    for enrollment in enrollments:
        recent_activity.append({
            'type': 'enrollment',
            'title': f'New enrollment in {enrollment.program.title}',
            'description': f'{enrollment.student.get_full_name()} enrolled',
            'date': enrollment.enrollment_date,
            'icon': 'fas fa-user-graduate'
        })
    
    # Pending Items
    pending_enrollments = Enrollment.objects.filter(
        program__instructor=teacher,
        status='pending'
    )[:5]
    
    # Upcoming Classes
    upcoming_classes = Class.objects.filter(
        program__instructor=teacher,
        start_time__gte=timezone.now()
    ).order_by('start_time')[:5]
    
    context = {
        'teacher': teacher,
        'total_students': total_students,
        'active_programs': active_programs,
        'total_courses': total_courses,
        'average_rating': average_rating,
        'user_growth': user_growth,
        'program_distribution': program_distribution,
        'enrollment_rate': enrollment_rate,
        'completion_rate': completion_rate,
        'recent_activity': recent_activity,
        'pending_enrollments': pending_enrollments,
        'upcoming_classes': upcoming_classes,
    }
    
    return render(request, 'enrollments/teacher/dashboard.html', context)

@login_required
def approve_enrollment(request, enrollment_id):
    """Approve a student's enrollment in a program."""
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, program__instructor=request.user)
    
    if enrollment.status == 'pending':
        enrollment.status = 'approved'
        enrollment.approved_by = request.user
        enrollment.approved_at = timezone.now()
        enrollment.save()
        
        messages.success(request, 'Enrollment approved successfully.')
    else:
        messages.error(request, 'This enrollment has already been processed.')
    
    return redirect('enrollments:teacher_dashboard')

@login_required
def reject_enrollment(request, enrollment_id):
    """Reject a student's enrollment in a program."""
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, program__instructor=request.user)
    
    if enrollment.status == 'pending':
        enrollment.status = 'rejected'
        enrollment.approved_by = request.user
        enrollment.approved_at = timezone.now()
        enrollment.save()
        
        messages.success(request, 'Enrollment rejected.')
    else:
        messages.error(request, 'This enrollment has already been processed.')
    
    return redirect('enrollments:teacher_dashboard')

@login_required
def program_progress_view(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, student=request.user)
    progress = CourseProgress.objects.filter(enrollment=enrollment)
    
    return render(request, 'enrollments/progress.html', {
        'enrollment': enrollment,
        'progress': progress
    })

@login_required
def check_access(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
    
    if enrollment and enrollment.can_access_course():
        return JsonResponse({'has_access': True})
    return JsonResponse({'has_access': False})

@login_required
def course_content_view(request, course_id):
    """
    View to display course content for enrolled students
    """
    course = get_object_or_404(Course, id=course_id, is_active=True)
    
    # Check if user is enrolled
    enrollment = course.course_enrollments.filter(
        student=request.user,
        status='approved'
    ).first()
    
    if not enrollment:
        messages.error(request, 'You must be enrolled in this course to view its content.')
        return redirect('enrollments:course_detail', course_id=course.id)
    
    # Get course content
    modules = course.program.modules.all().prefetch_related('lessons')
    
    # Get student's progress
    progress = CourseProgress.objects.filter(enrollment=enrollment)
    progress_dict = {p.lesson_id: p.status for p in progress}
    
    context = {
        'course': course,
        'modules': modules,
        'progress': progress_dict,
        'enrollment': enrollment,
    }
    return render(request, 'enrollments/course_content.html', context)

@login_required
def teacher_students(request):
    """Display a list of students enrolled in teacher's courses."""
    if request.user.role != 'teacher':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')
    
    courses = Course.objects.filter(instructor=request.user)
    students = User.objects.filter(
        student_enrollments__course__in=courses,
        student_enrollments__status='approved'
    ).distinct()
    
    return render(request, 'enrollments/teacher/students.html', {
        'students': students,
        'courses': courses
    })

@login_required
def teacher_assignments(request):
    """Display and manage assignments for teacher's courses."""
    if request.user.role != 'teacher':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')
    
    courses = Course.objects.filter(instructor=request.user)
    
    return render(request, 'enrollments/teacher/assignments.html', {
        'courses': courses
    })

@login_required
def student_assignments(request):
    """Display student's assignments across all enrolled courses."""
    if request.user.role != 'student':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('auth:dashboard')
    
    enrollments = Enrollment.objects.filter(
        student=request.user,
        status='approved'
    ).select_related('course')
    
    # Get assignments for all enrolled courses
    assignments = Assignment.objects.filter(
        course__in=[e.course for e in enrollments]
    ).select_related('course')
    
    # Get student's submissions
    submissions = AssignmentSubmission.objects.filter(
        student=request.user,
        assignment__in=assignments
    ).select_related('assignment')
    
    # Categorize assignments
    pending_assignments = assignments.exclude(
        id__in=submissions.values_list('assignment_id', flat=True)
    )
    
    submitted_assignments = submissions.filter(grade__isnull=True)
    graded_assignments = submissions.filter(grade__isnull=False)
    
    return render(request, 'enrollments/student/assignments.html', {
        'pending_assignments': pending_assignments,
        'submitted_assignments': submitted_assignments,
        'graded_assignments': graded_assignments
    })

@login_required
def student_certificates(request):
    """Display student's earned certificates."""
    if request.user.role != 'student':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('auth:dashboard')
    
    completed_enrollments = Enrollment.objects.filter(
        student=request.user,
        status='approved'
    ).annotate(
        completed_lessons=Count(
            'progress',
            filter=Q(progress__status='completed')
        )
    ).filter(completed_lessons__gt=0)
    
    return render(request, 'enrollments/student/certificates.html', {
        'completed_enrollments': completed_enrollments
    })

@login_required
def view_students(request):
    """Display a list of students enrolled in teacher's courses."""
    courses = Course.objects.filter(instructor=request.user)
    enrollments = CourseEnrollment.objects.filter(
        course__in=courses
    ).select_related('enrollment__student', 'course')
    
    context = {
        'courses': courses,
        'enrollments': enrollments
    }
    return render(request, 'enrollments/view_students.html', context) 
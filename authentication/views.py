from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test, REDIRECT_FIELD_NAME
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User, FAQ, VerificationCode, LoginAttempt, PasswordResetToken
from enrollments.models import Enrollment
from django.contrib.auth.hashers import make_password
import re
from django.db.models import Count, Q, Avg, Sum, Case, When, FloatField, Max, Min
from django.db.models.functions import TruncDate, Trunc
from enrollments.models import CourseProgress
from classes.models import Class
from blog.models import BlogPost
from .forms import (
    UserRegistrationForm, UserLoginForm, ProfileEditForm,
    CustomPasswordResetForm, CustomSetPasswordForm, CustomPasswordChangeForm,
    VirtualClassForm, TeacherJoinForm, StudentJoinForm
)
from django.utils import timezone
from django.db import models
from datetime import timedelta
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from profiles.forms import StudentProfileForm
from profiles.models import Profile, StudentProfile
from django.http import JsonResponse
from django.utils.http import url_has_allowed_host_and_scheme
import uuid
from .decorators import student_required, teacher_required
from programs.models import EducationalProgram
from programs.forms import ProgramForm
from zoom_integration.models import ZoomUser, ZoomMeeting, MeetingTemplate, MeetingFeedback, ZoomAttendance

# Template-based views
def home_view(request):
    """View for the home page."""
    context = {
        'page_title': 'Home',
        'page_description': 'Welcome to Edurise - Your Learning Platform'
    }
    return render(request, 'authentication/home.html', context)

def about(request):
    """View for the about page."""
    context = {
        'page_title': 'About Us',
        'page_description': 'Learn more about Edurise and our mission.'
    }
    return render(request, 'authentication/about.html', context)

def contact(request):
    """View for the contact page."""
    context = {
        'page_title': 'Contact Us',
        'page_description': 'Get in touch with us.'
    }
    return render(request, 'authentication/contact.html', context)

def faqs(request):
    """View for the FAQs page."""
    context = {
        'page_title': 'FAQs',
        'page_description': 'Frequently Asked Questions about Edurise.'
    }
    return render(request, 'authentication/faqs.html', context)

def guidelines(request):
    """View for the guidelines page."""
    context = {
        'page_title': 'Guidelines',
        'page_description': 'Learn about our platform guidelines and policies.'
    }
    return render(request, 'authentication/guidelines.html', context)

def login_view(request):
    """View for user login."""
    if request.user.is_authenticated:
        return redirect('auth:dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username_or_email']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me', False)
            user = authenticate(request, username=username_or_email, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful.')
                return redirect('auth:dashboard')
            else:
                messages.error(request, 'Invalid email or password.')
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = UserLoginForm()
    
    context = {
        'form': form,
        'page_title': 'Login',
        'page_description': 'Login to your account.'
    }
    return render(request, 'authentication/login.html', context)

def register_view(request):
    """View for user registration."""
    if request.user.is_authenticated:
        return redirect('auth:dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful. Please login.')
            return redirect('auth:login')
    else:
        form = UserRegistrationForm()
    
    context = {
        'form': form,
        'page_title': 'Register',
        'page_description': 'Create a new account.'
    }
    return render(request, 'authentication/register.html', context)

@login_required
def logout_view(request):
    """View for user logout."""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('auth:login')

@login_required
def dashboard(request):
    """View for the main dashboard."""
    if request.user.role == 'student':
        return redirect('auth:student_dashboard')
    elif request.user.role == 'teacher':
        return redirect('auth:teacher_dashboard')
    else:
        return redirect('admin_tools:dashboard')

@login_required
@student_required
def student_dashboard(request):
    """View for student dashboard."""
    enrollments = Enrollment.objects.filter(student=request.user, status='approved')
    context = {
        'enrollments': enrollments,
        'page_title': 'Student Dashboard',
        'page_description': 'Manage your learning journey.'
    }
    return render(request, 'authentication/student_dashboard.html', context)

@login_required
@teacher_required
def teacher_dashboard(request):
    teacher = request.user
    today = timezone.now().date()
    
    # Get upcoming classes
    upcoming_classes = Class.objects.filter(
        teacher=teacher,
        start_date__gte=today
    ).order_by('start_date')[:5]
    
    # Get recent enrollments
    recent_enrollments = Enrollment.objects.filter(
        program__instructor=teacher
    ).order_by('-created_at')[:5]
    
    # Get program statistics
    total_programs = EducationalProgram.objects.filter(instructor=teacher).count()
    active_programs = EducationalProgram.objects.filter(instructor=teacher, status='active').count()
    total_students = Enrollment.objects.filter(program__instructor=teacher).count()
    
    # Get Zoom integration data
    zoom_user = ZoomUser.objects.filter(user=teacher).first()
    upcoming_meetings = ZoomMeeting.objects.filter(
        teacher=teacher,
        start_time__gte=timezone.now()
    ).order_by('start_time')[:5]
    
    # Get meeting templates
    meeting_templates = MeetingTemplate.objects.filter(teacher=teacher)[:5]
    
    # Get recent meeting feedback
    recent_feedback = MeetingFeedback.objects.filter(
        meeting__teacher=teacher
    ).select_related('meeting', 'student').order_by('-created_at')[:5]
    
    # Get attendance statistics
    attendance_stats = ZoomAttendance.objects.filter(
        meeting__teacher=teacher,
        meeting__start_time__gte=timezone.now() - timedelta(days=7)
    ).aggregate(
        total_present=Count('id', filter=Q(status='present')),
        total_late=Count('id', filter=Q(status='late')),
        total_absent=Count('id', filter=Q(status='absent'))
    )
    
    context = {
        'upcoming_classes': upcoming_classes,
        'recent_enrollments': recent_enrollments,
        'total_programs': total_programs,
        'active_programs': active_programs,
        'total_students': total_students,
        'zoom_user': zoom_user,
        'upcoming_meetings': upcoming_meetings,
        'meeting_templates': meeting_templates,
        'recent_feedback': recent_feedback,
        'attendance_stats': attendance_stats,
    }
    
    return render(request, 'authentication/teacher_dashboard.html', context)

@login_required
def profile_view(request):
    """View for user profile."""
    context = {
        'page_title': 'My Profile',
        'page_description': 'View and manage your profile.'
    }
    return render(request, 'authentication/profile.html', context)

@login_required
def profile_edit(request):
    """View for editing user profile."""
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('auth:profile')
    else:
        form = ProfileEditForm(instance=request.user)
    
    context = {
        'form': form,
        'page_title': 'Edit Profile',
        'page_description': 'Update your profile information.'
    }
    return render(request, 'authentication/profile_edit.html', context)

@login_required
def settings_view(request):
    """View for user settings."""
    context = {
        'page_title': 'Settings',
        'page_description': 'Manage your account settings.'
    }
    return render(request, 'authentication/settings.html', context)

@login_required
def change_password(request):
    """View for changing password."""
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        if not request.user.check_password(old_password):
            messages.error(request, 'Current password is incorrect.')
        elif new_password1 != new_password2:
            messages.error(request, 'New passwords do not match.')
        else:
            request.user.set_password(new_password1)
            request.user.save()
            messages.success(request, 'Password changed successfully. Please login again.')
            return redirect('auth:login')
    
    context = {
        'page_title': 'Change Password',
        'page_description': 'Update your account password.'
    }
    return render(request, 'authentication/change_password.html', context)

def join_teacher(request):
    """View for teacher registration."""
    if request.method == 'POST':
        form = TeacherJoinForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'teacher'
            user.is_active = False
            user.is_approved = False
            user.save()
            # Save extra fields to profile if needed
            profile, created = Profile.objects.get_or_create(user=user)
            profile.education = form.cleaned_data['education']
            profile.experience = form.cleaned_data['experience']
            profile.expertise = form.cleaned_data['expertise']
            if form.cleaned_data.get('cv'):
                profile.cv = form.cleaned_data['cv']
            profile.save()
            messages.success(request, 'Teacher registration submitted. Awaiting admin approval.')
            return redirect('auth:login')
    else:
        form = TeacherJoinForm()

    context = {
        'form': form,
        'page_title': 'Join as Teacher',
        'page_description': 'Create a teacher account.'
    }
    return render(request, 'authentication/join_teacher.html', context)

def join_student(request):
    """View for student registration."""
    if request.method == 'POST':
        form = StudentJoinForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'student'
            user.is_active = False
            user.is_approved = False
            user.save()
            # Save extra fields to student profile
            student_profile, created = StudentProfile.objects.get_or_create(user=user)
            student_profile.age = form.cleaned_data['age']
            student_profile.interests = form.cleaned_data['interests']
            student_profile.save()
            messages.success(request, 'Student registration submitted. Awaiting admin approval.')
            return redirect('auth:login')
    else:
        form = StudentJoinForm()
    
    context = {
        'form': form,
        'page_title': 'Join as Student',
        'page_description': 'Create a student account.'
    }
    return render(request, 'authentication/join_student.html', context)

@login_required
def student_profile(request):
    """View for student profile."""
    context = {
        'page_title': 'Student Profile',
        'page_description': 'View and manage your student profile.'
    }
    return render(request, 'authentication/student_profile.html', context)

def programs(request):
    """View for browsing available programs."""
    programs = EducationalProgram.objects.filter(is_active=True)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        programs = programs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    context = {
        'programs': programs,
        'page_title': 'Programs',
        'page_description': 'Browse available educational programs.'
    }
    return render(request, 'authentication/programs.html', context)

@login_required
@student_required
def program_enrollment(request, program_id):
    """View for program enrollment."""
    program = get_object_or_404(EducationalProgram, id=program_id)
    
    # Check if already enrolled
    if Enrollment.objects.filter(student=request.user, program=program).exists():
        messages.info(request, 'You are already enrolled in this program.')
        return redirect('auth:programs')
    
    # Create enrollment
    Enrollment.objects.create(
        student=request.user,
        program=program,
        status='pending'
    )
    
    messages.success(request, 'Enrollment request submitted successfully.')
    return redirect('auth:student_dashboard')

def resend_verification(request):
    """View for resending verification email."""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                # Generate new verification code
                verification = VerificationCode.objects.create(user=user)
                # Send verification email
                try:
                    send_mail(
                        'Verify your email',
                        f'Click here to verify your email: {request.build_absolute_uri(reverse("auth:verify_email"))}?code={verification.code}',
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=False,
                    )
                    messages.success(request, 'Verification email sent. Please check your inbox.')
                except Exception as e:
                    messages.error(request, f'Failed to send verification email: {e}')
            else:
                messages.info(request, 'Your email is already verified.')
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email.')
    
    return redirect('auth:login')

@login_required
@teacher_required
def program_form(request, program_id=None):
    """View for creating or editing a program."""
    program = None
    if program_id:
        program = get_object_or_404(EducationalProgram, id=program_id)
        # Check if the user has permission to edit this program
        if program.teacher != request.user and not request.user.is_staff:
            messages.error(request, 'You do not have permission to edit this program.')
            return redirect('auth:programs')

    if request.method == 'POST':
        form = ProgramForm(request.POST, request.FILES, instance=program)
        if form.is_valid():
            program = form.save(commit=False)
            program.teacher = request.user
            program.save()
            messages.success(request, 'Program saved successfully!')
            return redirect('auth:programs')
    else:
        form = ProgramForm(instance=program)

    context = {
        'form': form,
        'program': program,
        'page_title': 'Create Program' if not program else 'Edit Program',
        'page_description': 'Create a new educational program' if not program else 'Edit existing program'
    }
    return render(request, 'authentication/program_form.html', context)

@login_required
def update_notifications(request):
    """View for updating notification preferences."""
    if request.method == 'POST':
        user = request.user
        user.email_notifications = request.POST.get('email_notifications') == 'on'
        user.sms_notifications = request.POST.get('sms_notifications') == 'on'
        user.course_updates = request.POST.get('course_updates') == 'on'
        user.receive_announcements = request.POST.get('announcements') == 'on'
        user.save()
        messages.success(request, 'Notification preferences updated successfully!')
    return redirect('auth:settings')

@login_required
def update_preferences(request):
    """View for updating user preferences."""
    if request.method == 'POST':
        user = request.user
        user.language = request.POST.get('language', 'en')
        user.timezone = request.POST.get('timezone', 'UTC')
        user.date_format = request.POST.get('date_format', 'MM/DD/YYYY')
        user.save()
        messages.success(request, 'Preferences updated successfully!')
    return redirect('auth:settings')

# API Views
class UserRegistrationView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationForm(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'User registered successfully.',
                'user_id': user.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)

class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
        })

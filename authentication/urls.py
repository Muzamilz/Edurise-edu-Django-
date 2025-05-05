from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import (
    home_view, about, contact, faqs, guidelines,
    dashboard, profile_view, logout_view, login_view, register_view,
    student_dashboard, teacher_dashboard, profile_edit, settings_view,
    student_profile, join_teacher, join_student,
    program_enrollment, change_password, programs
)

app_name = 'auth'

urlpatterns = [
    # Public pages
    path('', home_view, name='home'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('faqs/', faqs, name='faqs'),
    path('guidelines/', guidelines, name='guidelines'),
    path('programs/', programs, name='programs'),
    path('programs/<uuid:program_id>/enroll/', program_enrollment, name='program_enrollment'),
    
    # Authentication
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('change-password/', change_password, name='change_password'),
    
    # Password Reset URLs
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='authentication/password_reset.html',
        email_template_name='authentication/password_reset_email.html',
        subject_template_name='authentication/password_reset_subject.txt'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='authentication/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='authentication/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='authentication/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # User profiles and settings
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', profile_edit, name='profile_edit'),
    path('settings/', settings_view, name='settings'),
    
    # Role-specific pages
    path('dashboard/', dashboard, name='dashboard'),
    path('student/dashboard/', student_dashboard, name='student_dashboard'),
    path('teacher/dashboard/', teacher_dashboard, name='teacher_dashboard'),
    path('student/profile/', student_profile, name='student_profile'),
    path('join/teacher/', join_teacher, name='join_teacher'),
    path('join/student/', join_student, name='join_student'),
    path('update-notifications/', views.update_notifications, name='update_notifications'),
    path('update-preferences/', views.update_preferences, name='update_preferences'),
]

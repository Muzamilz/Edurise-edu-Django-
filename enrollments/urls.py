from django.urls import path
from . import views

app_name = 'enrollments'

urlpatterns = [
    path('programs/', views.program_list, name='program_list'),
    path('programs/<uuid:program_id>/', views.program_detail, name='program_detail'),
    path('programs/<uuid:program_id>/enroll/', views.enroll, name='enroll'),
    path('courses/<uuid:course_id>/', views.course_detail, name='course_detail'),
    path('my-enrollments/', views.my_enrollments, name='my_enrollments'),
    path('student/assignments/', views.student_assignments, name='student_assignments'),
    path('student/certificates/', views.student_certificates, name='student_certificates'),
    path('progress/<uuid:enrollment_id>/', views.course_progress, name='course_progress'),
    path('progress/<uuid:progress_id>/update/', views.update_progress, name='update_progress'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/students/', views.teacher_students, name='teacher_students'),
    path('teacher/assignments/', views.teacher_assignments, name='teacher_assignments'),
    path('enrollments/<uuid:enrollment_id>/', views.enrollment_detail, name='enrollment_detail'),
    path('enrollments/<uuid:enrollment_id>/approve/', views.approve_enrollment, name='approve_enrollment'),
    path('enrollments/<uuid:enrollment_id>/reject/', views.reject_enrollment, name='reject_enrollment'),
] 
from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('', views.profile_view, name='profile'),
    path('edit/', views.edit_profile, name='edit_profile'),
    path('teacher/', views.teacher_profile_view, name='teacher_profile'),
    path('teacher/edit/', views.edit_teacher_profile, name='edit_teacher_profile'),
    path('student/', views.student_profile_view, name='student_profile'),
    path('student/edit/', views.edit_student_profile, name='edit_student_profile'),
] 
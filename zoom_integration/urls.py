from django.urls import path
from . import views

app_name = 'zoom'

urlpatterns = [
    # Basic Zoom Integration
    path('connect/', views.connect_zoom, name='connect'),
    path('callback/', views.zoom_callback, name='callback'),
    path('create-meeting/', views.create_meeting, name='create_meeting'),
    path('meetings/', views.meeting_list, name='meeting_list'),
    path('meetings/<int:meeting_id>/', views.meeting_detail, name='meeting_detail'),
    path('upcoming-meetings/', views.upcoming_meetings, name='upcoming_meetings'),
    
    # Meeting Templates
    path('templates/create/', views.create_meeting_template, name='create_template'),
    path('templates/', views.template_list, name='template_list'),
    
    # Bulk Scheduling
    path('bulk-schedule/create/', views.create_bulk_schedule, name='create_bulk_schedule'),
    path('bulk-schedule/', views.bulk_schedule_list, name='bulk_schedule_list'),
    
    # Attendance Tracking
    path('meetings/<int:meeting_id>/attendance/', views.track_attendance, name='track_attendance'),
    
    # Resources and Feedback
    path('meetings/<int:meeting_id>/resources/', views.upload_meeting_resource, name='upload_resource'),
    path('meetings/<int:meeting_id>/feedback/', views.submit_meeting_feedback, name='submit_feedback'),
    
    # Analytics
    path('programs/<int:program_id>/analytics/', views.program_analytics, name='program_analytics'),
    path('update-analytics/', views.update_analytics, name='update_analytics'),
    path('meetings/<int:meeting_id>/analytics/', views.get_meeting_analytics, name='meeting_analytics'),

    path('virtual-classes/', views.virtual_class_list, name='virtual_class_list'),
    path('virtual-classes/create/', views.create_virtual_class, name='create_virtual_class'),
    path('virtual-classes/<int:class_id>/edit/', views.edit_virtual_class, name='edit_virtual_class'),
    path('virtual-classes/<int:class_id>/delete/', views.delete_virtual_class, name='delete_virtual_class'),
] 
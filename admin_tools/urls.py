from django.urls import path
from . import views

app_name = 'admin_tools'

urlpatterns = [
    # Public URLs
    path('announcements/', views.public_announcements, name='public_announcements'),
    path('announcements/list/', views.announcement_list, name='announcement_list'),
    
    # Admin-only URLs
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),  # Alias for reverse lookups
    path('users/', views.user_management, name='user_management'),
    path('users/activity-logs/', views.user_activity_logs, name='user_activity_logs'),
    path('users/permissions/', views.user_permissions, name='user_permissions'),
    path('users/sessions/', views.user_sessions, name='user_sessions'),
    path('users/bulk-operations/', views.bulk_user_operations, name='bulk_user_operations'),
    path('users/<uuid:user_id>/approve/', views.admin_approve_user, name='approve_user'),
    path('users/<uuid:user_id>/reject/', views.admin_reject_user, name='reject_user'),
    path('users/<uuid:user_id>/update-role/', views.update_user_role, name='update_user_role'),
    path('users/create/', views.admin_create_user, name='create_user'),
    path('users/<uuid:user_id>/edit/', views.edit_user, name='edit_user'),
    path('users/<uuid:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    
    # Content Management URLs
    path('content/', views.admin_content_moderation, name='content_moderation'),
    path('faqs/', views.admin_faqs, name='faqs'),
    
    # System Management URLs
    path('settings/', views.admin_settings, name='settings'),
    path('settings/', views.admin_settings, name='system_settings'),  # Alias for reverse lookups
    path('system/health/', views.system_health, name='system_health'),
    path('system/errors/', views.error_logs, name='error_logs'),
    path('system/api/', views.api_monitoring, name='api_monitoring'),
    
    # Analytics URLs
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('analytics/create/', views.create_report, name='create_report'),
    path('analytics/report/<int:report_id>/', views.view_report, name='view_report'),
    
    # Announcement Management URLs
    path('announcements/create/', views.create_announcement, name='create_announcement'),
    path('announcements/categories/', views.announcement_categories, name='announcement_categories'),
    path('announcements/settings/', views.announcement_settings, name='announcement_settings'),
    path('announcements/<int:announcement_id>/edit/', views.edit_announcement, name='edit_announcement'),
    path('announcements/<int:announcement_id>/delete/', views.delete_announcement, name='delete_announcement'),
    path('faq-management/', views.faq_management, name='faq_management'),
    path('add-role/', views.add_role, name='add_role'),
    path('audit-logs/', views.audit_logs, name='audit_logs'),
    path('add-group/', views.add_group, name='add_group'),
] 
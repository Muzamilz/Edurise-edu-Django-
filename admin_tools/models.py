from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class UserPermission(models.Model):
    PERMISSION_CHOICES = [
        ('can_manage_users', 'Can Manage Users'),
        ('can_manage_courses', 'Can Manage Courses'),
        ('can_manage_enrollments', 'Can Manage Enrollments'),
        ('can_view_reports', 'Can View Reports'),
        ('can_manage_settings', 'Can Manage Settings'),
        ('can_manage_content', 'Can Manage Content'),
        ('can_manage_analytics', 'Can Manage Analytics'),
        ('can_manage_system', 'Can Manage System'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='permissions')
    permission_name = models.CharField(max_length=50, choices=PERMISSION_CHOICES)
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='granted_permissions')
    granted_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'permission_name')
        verbose_name = 'User Permission'
        verbose_name_plural = 'User Permissions'

    def __str__(self):
        return f"{self.user.email} - {self.get_permission_name_display()}"

class UserActivityLog(models.Model):
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('profile_update', 'Profile Update'),
        ('password_change', 'Password Change'),
        ('role_change', 'Role Change'),
        ('permission_change', 'Permission Change'),
        ('enrollment', 'Enrollment'),
        ('course_access', 'Course Access'),
        ('content_access', 'Content Access'),
        ('report_generation', 'Report Generation'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    details = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'User Activity Log'
        verbose_name_plural = 'User Activity Logs'

    def __str__(self):
        return f"{self.user.email} - {self.get_action_display()} - {self.timestamp}"

class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-last_activity']
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'

    def __str__(self):
        return f"{self.user.email} - {self.session_key}"

class SystemHealthLog(models.Model):
    cpu_usage = models.FloatField()
    memory_usage = models.FloatField()
    disk_usage = models.FloatField()
    database_queries = models.IntegerField()
    response_time = models.FloatField()
    error_count = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'System Health Log'
        verbose_name_plural = 'System Health Logs'

    def __str__(self):
        return f"System Health Log - {self.timestamp}"

class ErrorLog(models.Model):
    ERROR_LEVELS = [
        ('debug', 'Debug'),
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    level = models.CharField(max_length=10, choices=ERROR_LEVELS)
    message = models.TextField()
    stack_trace = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Error Log'
        verbose_name_plural = 'Error Logs'

    def __str__(self):
        return f"{self.level} - {self.message[:50]}"

class APILog(models.Model):
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    status_code = models.IntegerField()
    response_time = models.FloatField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'API Log'
        verbose_name_plural = 'API Logs'

    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.status_code}"

class AnalyticsReport(models.Model):
    REPORT_TYPES = [
        ('user_growth', 'User Growth'),
        ('course_performance', 'Course Performance'),
        ('revenue', 'Revenue'),
        ('engagement', 'User Engagement'),
        ('custom', 'Custom Report'),
    ]

    name = models.CharField(max_length=100)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    parameters = models.JSONField(default=dict)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    last_run = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Analytics Report'
        verbose_name_plural = 'Analytics Reports'

    def __str__(self):
        return f"{self.name} ({self.get_report_type_display()})"

class AnalyticsData(models.Model):
    report = models.ForeignKey(AnalyticsReport, on_delete=models.CASCADE, related_name='data_points')
    data = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Analytics Data'
        verbose_name_plural = 'Analytics Data'

    def __str__(self):
        return f"Data for {self.report.name} - {self.timestamp}"

class AdminSetting(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['key']
        verbose_name = 'Admin Setting'
        verbose_name_plural = 'Admin Settings'

    def __str__(self):
        return f"{self.key}: {self.value[:50]}"

class AdminAuditLog(models.Model):
    ACTION_CHOICES = [
        ('create_user', 'Create User'),
        ('update_user', 'Update User'),
        ('delete_user', 'Delete User'),
        ('approve_user', 'Approve User'),
        ('reject_user', 'Reject User'),
        ('update_role', 'Update Role'),
        ('update_permission', 'Update Permission'),
        ('update_setting', 'Update Setting'),
        ('create_program', 'Create Program'),
        ('update_program', 'Update Program'),
        ('delete_program', 'Delete Program'),
        ('create_announcement', 'Create Announcement'),
        ('update_announcement', 'Update Announcement'),
        ('delete_announcement', 'Delete Announcement'),
    ]

    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_actions')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    entity_type = models.CharField(max_length=50)
    entity_id = models.CharField(max_length=50)
    details = models.TextField()
    target_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_audit_logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Admin Audit Log'
        verbose_name_plural = 'Admin Audit Logs'

    def __str__(self):
        return f"{self.admin.email} - {self.get_action_display()} - {self.timestamp}"

class AnnouncementCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Announcement Category'
        verbose_name_plural = 'Announcement Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

class Announcement(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.ForeignKey(AnnouncementCategory, on_delete=models.CASCADE, related_name='announcements')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_announcements')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Announcement'
        verbose_name_plural = 'Announcements'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def is_current(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date and self.is_active and self.status == 'published' 
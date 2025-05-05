from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
import uuid
from django.utils import timezone
from programs.models import EducationalProgram, Course
from django.conf import settings

User = get_user_model()

class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.BooleanField(default=False)
    payment_proof = models.FileField(blank=True, null=True, upload_to='payment_proofs/')
    payment_date = models.DateTimeField(blank=True, null=True)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    approved_date = models.DateTimeField(blank=True, null=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    additional_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Approval fields
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='approved_enrollments'
    )
    
    # Rejection fields
    rejected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='rejected_enrollments'
    )
    rejection_date = models.DateTimeField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    # Progress tracking
    start_date = models.DateTimeField(blank=True, null=True)
    completion_date = models.DateTimeField(blank=True, null=True)
    
    # Virtual Class Access
    zoom_access_granted = models.BooleanField(default=False)
    last_meeting_attended = models.DateTimeField(null=True, blank=True)
    attendance_rate = models.FloatField(default=0.0)
    meeting_reminders_enabled = models.BooleanField(default=True)
    calendar_sync_enabled = models.BooleanField(default=False)
    calendar_sync_token = models.TextField(null=True, blank=True)
    
    # Relationships
    program = models.ForeignKey(EducationalProgram, on_delete=models.CASCADE, related_name='enrollments')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')

    class Meta:
        ordering = ['-enrolled_at']
        unique_together = ['student', 'program']

    def __str__(self):
        return f"{self.student.username} - {self.program.name}"

    def save(self, *args, **kwargs):
        if self.status == 'approved' and not self.start_date:
            self.start_date = timezone.now()
            self.approved_date = timezone.now()
        if self.status == 'completed' and not self.completion_date:
            self.completion_date = timezone.now()
        super().save(*args, **kwargs)

    @property
    def is_pending(self):
        return self.status == 'pending'

    @property
    def is_active(self):
        return self.status == 'active'

    @property
    def is_completed(self):
        return self.status == 'completed'

    @property
    def is_cancelled(self):
        return self.status == 'cancelled'

    def grant_zoom_access(self):
        self.zoom_access_granted = True
        self.save()

    def revoke_zoom_access(self):
        self.zoom_access_granted = False
        self.save()

    def update_attendance_rate(self):
        from zoom_integration.models import ZoomAttendance
        meetings = self.program.zoom_meetings.filter(
            start_time__lte=timezone.now()
        )
        if not meetings:
            return
        
        total_meetings = meetings.count()
        attended_meetings = ZoomAttendance.objects.filter(
            meeting__in=meetings,
            student=self.student,
            status__in=['present', 'late']
        ).count()
        
        self.attendance_rate = (attended_meetings / total_meetings * 100) if total_meetings > 0 else 0
        self.save()

    def get_upcoming_meetings(self):
        return self.program.zoom_meetings.filter(
            start_time__gt=timezone.now()
        ).order_by('start_time')

    def get_meeting_history(self):
        return self.program.zoom_meetings.filter(
            start_time__lte=timezone.now()
        ).order_by('-start_time')

    def get_attendance_history(self):
        from zoom_integration.models import ZoomAttendance
        return ZoomAttendance.objects.filter(
            meeting__program=self.program,
            student=self.student
        ).order_by('-meeting__start_time')

class CourseEnrollment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]

    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)
    status = models.CharField(choices=STATUS_CHOICES, default='pending', max_length=20)
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='course_enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = [('enrollment', 'course')]

    def __str__(self):
        return f"{self.enrollment.student.username} - {self.course.title}"

class ProgramProgress(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    status = models.CharField(choices=STATUS_CHOICES, default='not_started', max_length=20)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    last_accessed = models.DateTimeField(auto_now=True)
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='progress')

    class Meta:
        ordering = ['-last_accessed']
        unique_together = [('enrollment',)]

    def __str__(self):
        return f"{self.enrollment.student.username} - {self.enrollment.program.title}"

    def save(self, *args, **kwargs):
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)

class CourseProgress(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    status = models.CharField(choices=STATUS_CHOICES, default='not_started', max_length=20)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    last_accessed = models.DateTimeField(auto_now=True)
    course_enrollment = models.ForeignKey(CourseEnrollment, on_delete=models.CASCADE, related_name='progress')

    class Meta:
        ordering = ['-last_accessed']
        unique_together = [('course_enrollment',)]

    def __str__(self):
        return f"{self.course_enrollment.enrollment.student.username} - {self.course_enrollment.course.title}"

    def save(self, *args, **kwargs):
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs) 
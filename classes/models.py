import uuid
from django.db import models
from django.conf import settings
from programs.models import EducationalProgram
from django.utils import timezone

class Resource(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    file = models.FileField(upload_to='class_resources/')
    category = models.CharField(max_length=100)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='class_resources')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

class Class(models.Model):
    program = models.ForeignKey(EducationalProgram, on_delete=models.CASCADE, related_name='classes')
    title = models.CharField(max_length=200)
    description = models.TextField()
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='teaching_classes')
    students = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='enrolled_classes')
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Zoom Integration
    zoom_meeting = models.ForeignKey('zoom_integration.ZoomMeeting', on_delete=models.SET_NULL, null=True, blank=True, related_name='class_meetings')
    recording_url = models.URLField(null=True, blank=True)
    resources = models.ManyToManyField(Resource, related_name='classes')
    meeting_notes = models.TextField(blank=True)
    feedback_enabled = models.BooleanField(default=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name_plural = 'Classes'

    def __str__(self):
        return f"{self.title} - {self.program.title}"
    
    @property
    def is_active(self):
        return self.start_date <= timezone.now().date() <= self.end_date
    
    @property
    def student_count(self):
        return self.students.count()
    
    @property
    def resource_count(self):
        return self.resources.count()
    
    @property
    def has_recording(self):
        return bool(self.recording_url)
    
    def get_student_feedback(self):
        return self.feedback_set.all().order_by('-created_at')
    
    def get_attendance_stats(self):
        if not self.zoom_meeting:
            return None
        return self.zoom_meeting.get_attendance_stats()

class Feedback(models.Model):
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='class_feedbacks')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['class_instance', 'student']
    
    def __str__(self):
        return f"Feedback from {self.student.username} for {self.class_instance.title}"

class ClassAttendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='attendance')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='class_attendance')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='absent')
    join_time = models.DateTimeField(null=True, blank=True)
    leave_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['class_instance', 'student']
        indexes = [
            models.Index(fields=['class_instance']),
            models.Index(fields=['student']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.student.username} - {self.class_instance.title}"

class ClassFeedback(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='feedback')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='class_feedback')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    feedback = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['class_instance', 'student']
        indexes = [
            models.Index(fields=['class_instance']),
            models.Index(fields=['student']),
            models.Index(fields=['rating']),
        ]

    def __str__(self):
        return f"{self.student.username} - {self.class_instance.title} - {self.rating}" 
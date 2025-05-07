from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from programs.models import EducationalProgram
from django.utils import timezone

User = get_user_model()

class MeetingTemplate(models.Model):
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='meeting_templates')
    program = models.ForeignKey(EducationalProgram, on_delete=models.CASCADE, related_name='zoom_meeting_templates')
    name = models.CharField(max_length=255)
    topic = models.CharField(max_length=255)
    duration = models.IntegerField(help_text="Duration in minutes")
    settings = models.JSONField(default=dict, help_text="Zoom meeting settings")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.program.title}"

class BulkMeetingSchedule(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bulk_schedules')
    program = models.ForeignKey(EducationalProgram, on_delete=models.CASCADE, related_name='bulk_schedules')
    template = models.ForeignKey(MeetingTemplate, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    days_of_week = models.JSONField(help_text="List of days (0-6, where 0 is Monday)")
    time_slots = models.JSONField(help_text="List of time slots in HH:MM format")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_meetings = models.ManyToManyField('ZoomMeeting', related_name='bulk_schedules')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Bulk Schedule for {self.program.name} - {self.start_date} to {self.end_date}"
    
    def get_progress(self):
        total = len(self.created_meetings.all())
        completed = self.created_meetings.filter(start_time__lt=timezone.now()).count()
        return (completed / total * 100) if total > 0 else 0

class Resource(models.Model):
    meeting = models.ForeignKey('ZoomMeeting', on_delete=models.CASCADE, related_name='zoom_resources')
    name = models.CharField(max_length=200)
    description = models.TextField()
    file = models.FileField(upload_to='meeting_resources/')
    category = models.CharField(max_length=100)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='zoom_resources')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

class MeetingFeedback(models.Model):
    meeting = models.ForeignKey('ZoomMeeting', on_delete=models.CASCADE, related_name='feedback')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['meeting', 'student']
    
    def __str__(self):
        return f"Feedback from {self.student.username} for {self.meeting.topic}"

class ZoomMeeting(models.Model):
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='zoom_meetings')
    program = models.ForeignKey(EducationalProgram, on_delete=models.CASCADE, related_name='zoom_meetings')
    class_instance = models.ForeignKey('classes.Class', on_delete=models.SET_NULL, null=True, blank=True, related_name='zoom_meetings')
    topic = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    duration = models.IntegerField(help_text="Duration in minutes")
    zoom_meeting_id = models.CharField(max_length=100)
    join_url = models.URLField()
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    template = models.ForeignKey(MeetingTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    bulk_schedule = models.ForeignKey(BulkMeetingSchedule, on_delete=models.SET_NULL, null=True, blank=True)
    feedback_enabled = models.BooleanField(default=True)

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.topic} - {self.start_time}"

    def get_feedback_stats(self):
        feedback = self.feedback.all()
        if not feedback:
            return None
        
        total_ratings = feedback.count()
        avg_rating = feedback.aggregate(models.Avg('rating'))['rating__avg']
        
        return {
            'total_feedback': total_ratings,
            'average_rating': round(avg_rating, 1) if avg_rating else 0,
            'rating_distribution': {
                i: feedback.filter(rating=i).count() for i in range(1, 6)
            }
        }
    
    def get_attendance_stats(self):
        attendance = self.attendance.all()
        if not attendance:
            return None
        
        total_students = attendance.count()
        present = attendance.filter(status='present').count()
        late = attendance.filter(status='late').count()
        absent = attendance.filter(status='absent').count()
        
        return {
            'total_students': total_students,
            'present': present,
            'late': late,
            'absent': absent,
            'attendance_rate': ((present + late) / total_students * 100) if total_students > 0 else 0
        }

class ZoomUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    zoom_user_id = models.CharField(max_length=100)
    access_token = models.TextField()
    refresh_token = models.TextField()
    token_expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Zoom Account"

class ZoomAttendance(models.Model):
    meeting = models.ForeignKey(ZoomMeeting, on_delete=models.CASCADE, related_name='attendance')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='zoom_attendance')
    join_time = models.DateTimeField()
    leave_time = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(help_text="Duration in minutes", null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('present', 'Present'),
        ('late', 'Late'),
        ('absent', 'Absent'),
        ('excused', 'Excused')
    ])

    class Meta:
        unique_together = ('meeting', 'student')

    def __str__(self):
        return f"{self.student.username} - {self.meeting.topic}"

class ZoomAnalytics(models.Model):
    program = models.ForeignKey(EducationalProgram, on_delete=models.CASCADE, related_name='zoom_analytics')
    date = models.DateField()
    total_meetings = models.IntegerField(default=0)
    total_participants = models.IntegerField(default=0)
    average_duration = models.IntegerField(default=0)
    total_attendance = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('program', 'date')

    def __str__(self):
        return f"{self.program.name} - {self.date}" 

class VirtualClass(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    program = models.ForeignKey('programs.EducationalProgram', on_delete=models.CASCADE, related_name='virtual_classes')
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='virtual_classes')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    meeting_link = models.URLField(max_length=500)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_time']
        verbose_name = 'Virtual Class'
        verbose_name_plural = 'Virtual Classes'

    def __str__(self):
        return f"{self.title} - {self.start_time}"

    @property
    def is_active(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time and self.status == 'in_progress'

    @property
    def is_upcoming(self):
        return self.start_time > timezone.now() and self.status == 'scheduled'

    @property
    def is_past(self):
        now = timezone.now()
        return now > self.end_time or self.status in ['completed', 'cancelled']

# Add the VirtualClass model from programs/models.py here, with all its methods and properties. 
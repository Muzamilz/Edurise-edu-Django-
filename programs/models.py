from django.db import models
import uuid
from django.utils import timezone
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()

class EducationalProgram(models.Model):
    PROGRAM_TYPE_CHOICES = [
        ('regular_english', 'Regular English Program'),
        ('plus_english', 'Plus English Program'),
        ('esp', 'English for Specific Purposes Program (ESP)'),
        ('eap', 'English for Academic Purposes Program (EAP)'),
        ('test_prep', 'International English Test Preparation Programs'),
        ('non_english', 'Non-English Language Programs'),
    ]

    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    program_type = models.CharField(max_length=20, choices=PROGRAM_TYPE_CHOICES)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    duration = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cover_photo = models.ImageField(upload_to='program_covers/', blank=True, null=True)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='programs_taught')
    students = models.ManyToManyField(User, related_name='enrolled_programs', blank=True)
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Virtual Class Settings
    virtual_class_enabled = models.BooleanField(default=False)
    zoom_settings = models.JSONField(default=dict, help_text="Program-specific Zoom settings")
    default_meeting_duration = models.IntegerField(default=60, help_text="Default meeting duration in minutes")
    max_participants = models.IntegerField(default=100, help_text="Maximum participants per meeting")
    meeting_templates = models.JSONField(default=list, help_text="Saved meeting templates")
    recording_settings = models.JSONField(default=dict, help_text="Recording preferences and settings")
    resource_categories = models.JSONField(default=list, help_text="Resource categories for the program")

    def __str__(self):
        return self.title

    def get_program_type_display(self):
        return dict(self.PROGRAM_TYPE_CHOICES).get(self.program_type, self.program_type)

    def get_level_display(self):
        return dict(self.LEVEL_CHOICES).get(self.level, self.level)

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    class Meta:
        ordering = ['-created_at']

    @property
    def active_meetings_count(self):
        return self.zoom_meetings.filter(
            start_time__lte=timezone.now(),
            start_time__gte=timezone.now() - timezone.timedelta(hours=1)
        ).count()
    
    @property
    def total_meetings_count(self):
        return self.zoom_meetings.count()
    
    @property
    def average_attendance_rate(self):
        from zoom_integration.models import ZoomAttendance
        meetings = self.zoom_meetings.all()
        if not meetings:
            return 0
        total_attendance = ZoomAttendance.objects.filter(meeting__in=meetings).count()
        total_possible = meetings.count() * self.students.count()
        return (total_attendance / total_possible * 100) if total_possible > 0 else 0

class Course(models.Model):
    """Model representing a course within a program."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    program = models.ForeignKey(EducationalProgram, on_delete=models.CASCADE, related_name='courses')
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.PositiveIntegerField()
    duration = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cover_photo = models.ImageField(upload_to='course_covers/', blank=True, null=True)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses_taught')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.program.title} - {self.title}"

    class Meta:
        ordering = ['order']
        unique_together = ['program', 'order']

class ProgramModule(models.Model):
    """Model representing a module within an educational program."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    program = models.ForeignKey(EducationalProgram, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.program.title} - {self.title}"

    class Meta:
        ordering = ['order']
        unique_together = ['program', 'order']

class ProgramLesson(models.Model):
    """Model representing a lesson within a program module."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module = models.ForeignKey(ProgramModule, on_delete=models.CASCADE, related_name='lessons')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons', null=True, blank=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    order = models.PositiveIntegerField()
    video_url = models.URLField(blank=True, null=True)
    duration = models.DurationField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.module.title} - {self.title}"

    class Meta:
        ordering = ['order']
        unique_together = ['module', 'order']

class ProgramRating(models.Model):
    """Model representing a rating for a program."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    program = models.ForeignKey(EducationalProgram, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='program_ratings')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['program', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.program.title} - {self.rating}"

class Lesson(models.Model):
    """Model for individual lessons within a program."""
    title = models.CharField(max_length=200)
    description = models.TextField()
    content = models.TextField()
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    order = models.PositiveIntegerField(
        default=0,
        help_text="Order of the lesson in the program"
    )
    scheduled_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this lesson is scheduled to be available"
    )
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Relationships
    program = models.ForeignKey(
        EducationalProgram,
        on_delete=models.CASCADE,
        related_name='lessons'
    )
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='lessons_created'
    )
    
    class Meta:
        ordering = ['order', 'created_at']
        unique_together = ['program', 'order']
    
    def __str__(self):
        return f"{self.program.title} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.order:
            # Set order to be the last in the program
            last_order = Lesson.objects.filter(program=self.program).aggregate(
                models.Max('order')
            )['order__max'] or 0
            self.order = last_order + 1
        super().save(*args, **kwargs)

class LessonProgress(models.Model):
    """Model to track student progress in individual lessons."""
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lesson_progress'
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='progress'
    )
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    progress_percentage = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    last_accessed = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'lesson']
        ordering = ['-last_accessed']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.lesson.title}"
    
    def save(self, *args, **kwargs):
        if self.is_completed and not self.completed_at:
            self.completed_at = timezone.now()
            self.progress_percentage = 100
        super().save(*args, **kwargs)
    
    @property
    def is_in_progress(self):
        return self.progress_percentage > 0 and not self.is_completed
    
    @property
    def time_spent(self):
        """Calculate time spent on the lesson in minutes"""
        if self.completed_at and self.created_at:
            return (self.completed_at - self.created_at).total_seconds() / 60
        return 0

class Term(models.Model):
    """Model representing an academic term."""
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Term'
        verbose_name_plural = 'Terms'

    def __str__(self):
        return self.name

    @property
    def is_current(self):
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date and self.is_active

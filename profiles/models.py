from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')

    def __str__(self):
        return f"{self.user.email}'s Profile"

class TeacherProfile(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='teacher_profile')
    teaching_experience = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text=_('Years of teaching experience')
    )
    specialization = models.CharField(max_length=100)
    qualifications = models.TextField()
    subjects = models.JSONField(default=list)
    teaching_style = models.CharField(max_length=100, blank=True)
    availability = models.JSONField(default=dict)
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Teacher Profile')
        verbose_name_plural = _('Teacher Profiles')

    def __str__(self):
        return f"{self.profile.user.email}'s Teacher Profile"

class StudentProfile(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='student_profile')
    learning_goals = models.TextField()
    preferred_languages = models.JSONField(default=list)
    skill_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', _('Beginner')),
            ('intermediate', _('Intermediate')),
            ('advanced', _('Advanced'))
        ]
    )
    interests = models.JSONField(default=list)
    learning_style = models.CharField(max_length=100, blank=True)
    time_zone = models.CharField(max_length=50, blank=True)
    preferred_schedule = models.JSONField(default=dict)

    class Meta:
        verbose_name = _('Student Profile')
        verbose_name_plural = _('Student Profiles')

    def __str__(self):
        return f"{self.profile.user.email}'s Student Profile" 
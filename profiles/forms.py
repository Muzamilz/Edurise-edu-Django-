from django import forms
from django.contrib.auth import get_user_model
from .models import Profile, TeacherProfile, StudentProfile

User = get_user_model()

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'location', 'website']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
        }

class AvatarUploadForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }

class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = [
            'teaching_experience',
            'specialization',
            'qualifications',
            'subjects',
            'teaching_style',
            'availability',
            'hourly_rate',
        ]
        widgets = {
            'teaching_experience': forms.NumberInput(attrs={'class': 'form-control'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'qualifications': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'subjects': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'teaching_style': forms.TextInput(attrs={'class': 'form-control'}),
            'availability': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'hourly_rate': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = [
            'learning_goals',
            'preferred_languages',
            'skill_level',
            'interests',
            'learning_style',
            'time_zone',
            'preferred_schedule',
        ]
        widgets = {
            'learning_goals': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'preferred_languages': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'skill_level': forms.Select(attrs={'class': 'form-control'}),
            'interests': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'learning_style': forms.TextInput(attrs={'class': 'form-control'}),
            'time_zone': forms.TextInput(attrs={'class': 'form-control'}),
            'preferred_schedule': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        } 
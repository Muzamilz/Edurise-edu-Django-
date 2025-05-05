from django import forms
from .models import EducationalProgram

class ProgramForm(forms.ModelForm):
    class Meta:
        model = EducationalProgram
        fields = [
            'title', 'description', 'program_type', 'level', 'duration', 'price',
            'cover_photo', 'instructor', 'is_active', 'status', 'start_date', 'end_date',
            'virtual_class_enabled', 'zoom_settings', 'default_meeting_duration',
            'max_participants', 'meeting_templates', 'recording_settings', 'resource_categories'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'zoom_settings': forms.Textarea(attrs={'rows': 2}),
            'meeting_templates': forms.Textarea(attrs={'rows': 2}),
            'recording_settings': forms.Textarea(attrs={'rows': 2}),
            'resource_categories': forms.Textarea(attrs={'rows': 2}),
        } 
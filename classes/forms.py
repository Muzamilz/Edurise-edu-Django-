from django import forms
from .models import Class, ClassAttendance, ClassFeedback

class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['program', 'title', 'description', 'start_date', 'end_date', 'teacher']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'program': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'teacher': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError("End date must be after start date")

        return cleaned_data

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = ClassAttendance
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = ClassFeedback
        fields = ['rating', 'feedback']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'class': 'form-control'}),
            'feedback': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        } 
from django import forms
from django.core.validators import MinValueValidator
from .models import Enrollment, CourseProgress
from programs.models import EducationalProgram, Course

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['payment_proof', 'additional_notes']
        widgets = {
            'payment_proof': forms.FileInput(attrs={'class': 'form-control'}),
            'additional_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Add any additional information or questions here...'
            })
        }
        labels = {
            'payment_proof': 'Payment Proof (Screenshot/Receipt)',
            'additional_notes': 'Additional Notes'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payment_proof'].required = True
        self.fields['payment_proof'].widget.attrs.update({
            'accept': 'image/*,.pdf',
            'class': 'form-control'
        })

class CourseProgressForm(forms.ModelForm):
    class Meta:
        model = CourseProgress
        fields = ['status', 'completed_at']
        widgets = {
            'completed_at': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].choices = [
            ('not_started', 'Not Started'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
        ]

    terms_accepted = forms.BooleanField(
        required=True,
        label='I agree to the Terms and Conditions',
        help_text='You must agree to the terms and conditions to enroll in this course.'
    )

    def clean_terms_accepted(self):
        terms_accepted = self.cleaned_data.get('terms_accepted')
        if not terms_accepted:
            raise forms.ValidationError('You must agree to the terms and conditions.')
        return terms_accepted 
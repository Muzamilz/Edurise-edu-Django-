from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import User
from programs.models import EducationalProgram
from zoom_integration.models import VirtualClass

User = get_user_model()

class UserLoginForm(forms.Form):
    username_or_email = forms.CharField(
        label='Email or Username',
        widget=forms.TextInput()
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput()
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput()
    )

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(label='Email')
    username = forms.CharField(label='Username')
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)
    password1 = forms.CharField(label='Password')
    password2 = forms.CharField(label='Confirm Password')

    class Meta:
        model = User
        fields = ('email', 'username', 'role', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(max_length=254)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise ValidationError(_('No account found with this email address.'))
        return email

class CustomSetPasswordForm(SetPasswordForm):
    pass

class CustomPasswordChangeForm(PasswordChangeForm):
    pass

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'bio', 'profile_picture']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

class ProgramForm(forms.ModelForm):
    class Meta:
        model = EducationalProgram
        fields = [
            'title', 'description', 'program_type', 'level', 
            'duration', 'price', 'cover_photo', 'instructor', 
            'status', 'start_date', 'end_date'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter instructors to only show active teachers
        self.fields['instructor'].queryset = User.objects.filter(
            role='teacher', 
            is_active=True, 
            is_approved=True
        )

class VirtualClassForm(forms.ModelForm):
    class Meta:
        model = VirtualClass
        fields = [
            'program', 'title', 'description', 'instructor',
            'start_time', 'end_time', 'status'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter instructors to only show active teachers
        self.fields['instructor'].queryset = User.objects.filter(
            role='teacher', 
            is_active=True, 
            is_approved=True
        )

class StudentJoinForm(UserCreationForm):
    age = forms.IntegerField(required=True, min_value=10, max_value=100)
    interests = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2', 'age', 'interests']

class TeacherJoinForm(UserCreationForm):
    education = forms.CharField(required=True, max_length=255)
    experience = forms.CharField(required=True, widget=forms.Textarea(attrs={'rows': 2}))
    expertise = forms.CharField(required=True, max_length=255)
    cv = forms.FileField(required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2', 'education', 'experience', 'expertise', 'cv'] 
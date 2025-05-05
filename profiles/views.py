from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile, TeacherProfile, StudentProfile
from .forms import ProfileEditForm, AvatarUploadForm, TeacherProfileForm, StudentProfileForm

@login_required
def profile_view(request):
    """View for displaying the user's profile."""
    profile = get_object_or_404(Profile, user=request.user)
    context = {
        'profile': profile,
        'is_teacher': hasattr(request.user, 'teacher_profile'),
        'is_student': hasattr(request.user, 'student_profile'),
    }
    return render(request, 'profiles/profile.html', context)

@login_required
def edit_profile(request):
    """View for editing the user's profile."""
    profile = get_object_or_404(Profile, user=request.user)
    
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profiles:profile')
    else:
        form = ProfileEditForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile,
    }
    return render(request, 'profiles/edit_profile.html', context)

@login_required
def upload_avatar(request):
    """View for uploading profile avatar."""
    profile = get_object_or_404(Profile, user=request.user)
    
    if request.method == 'POST':
        form = AvatarUploadForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Avatar updated successfully!')
            return redirect('profiles:profile')
    else:
        form = AvatarUploadForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile,
    }
    return render(request, 'profiles/upload_avatar.html', context)

@login_required
def teacher_profile_view(request):
    """View for displaying teacher profile."""
    if not hasattr(request.user, 'teacher_profile'):
        messages.error(request, 'You do not have a teacher profile.')
        return redirect('profiles:profile')
    
    teacher_profile = request.user.teacher_profile
    context = {
        'teacher_profile': teacher_profile,
    }
    return render(request, 'profiles/teacher_profile.html', context)

@login_required
def edit_teacher_profile(request):
    """View for editing teacher profile."""
    if not hasattr(request.user, 'teacher_profile'):
        messages.error(request, 'You do not have a teacher profile.')
        return redirect('profiles:profile')
    
    teacher_profile = request.user.teacher_profile
    
    if request.method == 'POST':
        form = TeacherProfileForm(request.POST, instance=teacher_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Teacher profile updated successfully!')
            return redirect('profiles:teacher_profile')
    else:
        form = TeacherProfileForm(instance=teacher_profile)
    
    context = {
        'form': form,
        'teacher_profile': teacher_profile,
    }
    return render(request, 'profiles/edit_teacher_profile.html', context)

@login_required
def student_profile_view(request):
    """View for displaying student profile."""
    if not hasattr(request.user, 'student_profile'):
        messages.error(request, 'You do not have a student profile.')
        return redirect('profiles:profile')
    
    student_profile = request.user.student_profile
    context = {
        'student_profile': student_profile,
    }
    return render(request, 'profiles/student_profile.html', context)

@login_required
def edit_student_profile(request):
    """View for editing student profile."""
    if not hasattr(request.user, 'student_profile'):
        messages.error(request, 'You do not have a student profile.')
        return redirect('profiles:profile')
    
    student_profile = request.user.student_profile
    
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, instance=student_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student profile updated successfully!')
            return redirect('profiles:student_profile')
    else:
        form = StudentProfileForm(instance=student_profile)
    
    context = {
        'form': form,
        'student_profile': student_profile,
    }
    return render(request, 'profiles/edit_student_profile.html', context)

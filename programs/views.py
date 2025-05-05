from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import EducationalProgram, ProgramModule, ProgramLesson, Course, ProgramRating
from classes.models import Class
from django.db.models import Q, Avg
from django.utils import timezone
from authentication.models import User
from datetime import timedelta

def is_admin_or_teacher(user):
    return user.role in ['admin', 'teacher']

@login_required
def enroll(request, program_id):
    """Handle program enrollment for students."""
    program = get_object_or_404(EducationalProgram, id=program_id)
    
    # Check if user is already enrolled
    if program.students.filter(id=request.user.id).exists():
        messages.warning(request, 'You are already enrolled in this program.')
        return redirect('programs:program_detail', program_id=program.id)
    
    # Check if program is active
    if not program.is_active or program.status != 'active':
        messages.error(request, 'This program is not currently available for enrollment.')
        return redirect('programs:program_detail', program_id=program.id)
    
    # Add student to program
    program.students.add(request.user)
    messages.success(request, 'Successfully enrolled in the program!')
    
    return redirect('programs:program_detail', program_id=program.id)

def program_list(request):
    """Display all available programs."""
    programs = EducationalProgram.objects.filter(status='active', is_active=True)
    return render(request, 'programs/program_list.html', {'programs': programs})

def program_detail(request, program_id):
    """Display details of a specific program."""
    program = get_object_or_404(EducationalProgram, id=program_id)
    modules = program.modules.all().order_by('order')
    courses = program.courses.all().order_by('order')
    ratings = program.ratings.all()
    
    # Calculate average rating
    avg_rating = ratings.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
    
    # Check if user is enrolled
    is_enrolled = request.user.is_authenticated and program.students.filter(id=request.user.id).exists()
    
    context = {
        'program': program,
        'modules': modules,
        'courses': courses,
        'ratings': ratings,
        'avg_rating': avg_rating,
        'is_enrolled': is_enrolled,
    }
    return render(request, 'programs/program_detail.html', context)

@login_required
@user_passes_test(is_admin_or_teacher)
def create_program(request):
    """Create a new educational program."""
    if request.method == 'POST':
        # Get form data
        title = request.POST.get('title')
        description = request.POST.get('description')
        program_type = request.POST.get('program_type')
        level = request.POST.get('level')
        duration = request.POST.get('duration')
        price = request.POST.get('price')
        instructor_id = request.POST.get('instructor')
        status = request.POST.get('status')
        cover_photo = request.FILES.get('cover_photo')
        
        # Get instructor
        instructor = get_object_or_404(User, id=instructor_id)
        
        # Create program
        program = EducationalProgram.objects.create(
            title=title,
            description=description,
            program_type=program_type,
            level=level,
            duration=duration,
            price=price,
            instructor=instructor,
            status=status,
            cover_photo=cover_photo
        )
        
        # Create a corresponding class for the program
        now = timezone.now()
        class_title = f"{title} - First Session"
        class_description = f"First class for the program: {description[:100]}..."
        Class.objects.create(
            program=program,
            teacher=instructor,
            title=class_title,
            description=class_description,
            start_time=now,
            end_time=now + timedelta(hours=1),
            status='scheduled'
        )
        
        messages.success(request, 'Program and its first class created successfully!')
        return redirect('programs:program_detail', program_id=program.id)
    
    # Get all teachers for the instructor dropdown
    teachers = User.objects.filter(role='teacher', is_active=True, is_approved=True)
    return render(request, 'programs/create_program.html', {'teachers': teachers})

@login_required
@user_passes_test(is_admin_or_teacher)
def edit_program(request, program_id):
    """Edit an existing educational program."""
    program = get_object_or_404(EducationalProgram, id=program_id)
    
    if request.method == 'POST':
        # Update program
        program.title = request.POST.get('title')
        program.description = request.POST.get('description')
        program.program_type = request.POST.get('program_type')
        program.level = request.POST.get('level')
        program.duration = request.POST.get('duration')
        program.price = request.POST.get('price')
        program.save()
        
        messages.success(request, 'Program updated successfully!')
        return redirect('programs:program_detail', program_id=program.id)
    
    return render(request, 'programs/edit_program.html', {'program': program})

@login_required
@user_passes_test(is_admin_or_teacher)
def delete_program(request, program_id):
    """Delete an educational program."""
    program = get_object_or_404(EducationalProgram, id=program_id)
    
    if request.method == 'POST':
        program.delete()
        messages.success(request, 'Program deleted successfully!')
        return redirect('programs:program_list')
    
    return render(request, 'programs/delete_program.html', {'program': program})

def program_type_list(request, program_type):
    """Display programs of a specific type."""
    programs = EducationalProgram.objects.filter(
        program_type=program_type,
        status='active',
        is_active=True
    )
    return render(request, 'programs/program_type_list.html', {
        'programs': programs,
        'program_type': program_type
    })

def regular_english(request):
    return program_type_list(request, 'regular_english')

def plus_english(request):
    return program_type_list(request, 'plus_english')

def esp(request):
    return program_type_list(request, 'esp')

def eap(request):
    return program_type_list(request, 'eap')

def test_prep(request):
    return program_type_list(request, 'test_prep')

def non_english(request):
    return program_type_list(request, 'non_english')

def ielts(request):
    """Display IELTS preparation programs."""
    programs = EducationalProgram.objects.filter(
        program_type='test_prep',
        title__icontains='ielts',
        status='active',
        is_active=True
    )
    return render(request, 'programs/ielts.html', {
        'programs': programs,
        'program_type': 'IELTS Preparation'
    })

def toefl(request):
    """Display TOEFL preparation programs."""
    programs = EducationalProgram.objects.filter(
        program_type='test_prep',
        title__icontains='toefl',
        status='active',
        is_active=True
    )
    return render(request, 'programs/toefl.html', {
        'programs': programs,
        'program_type': 'TOEFL Preparation'
    })

def business_english(request):
    """Display Business English programs."""
    programs = EducationalProgram.objects.filter(
        program_type='esp',
        title__icontains='business',
        status='active',
        is_active=True
    )
    return render(request, 'programs/business_english.html', {
        'programs': programs,
        'program_type': 'Business English'
    })

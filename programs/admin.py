from django.contrib import admin
from .models import (
    EducationalProgram,
    ProgramModule,
    ProgramLesson,
    Course,
    ProgramRating
)

@admin.register(EducationalProgram)
class EducationalProgramAdmin(admin.ModelAdmin):
    list_display = ('title', 'program_type', 'level', 'status', 'is_active')
    list_filter = ('program_type', 'level', 'status', 'is_active')
    search_fields = ('title', 'description')

@admin.register(ProgramModule)
class ProgramModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'program', 'order', 'is_active')
    list_filter = ('program', 'is_active')
    search_fields = ('title', 'description')

@admin.register(ProgramLesson)
class ProgramLessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'order', 'is_active')
    list_filter = ('module__program', 'is_active')
    search_fields = ('title', 'content')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'program', 'order', 'is_active')
    list_filter = ('program', 'is_active')
    search_fields = ('title', 'description')

@admin.register(ProgramRating)
class ProgramRatingAdmin(admin.ModelAdmin):
    list_display = ('program', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('program__title', 'user__username', 'review')

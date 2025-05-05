from django.urls import path
from . import views

app_name = 'programs'

urlpatterns = [
    path('', views.program_list, name='program_list'),
    path('create/', views.create_program, name='create_program'),
    path('<uuid:program_id>/', views.program_detail, name='program_detail'),
    path('<uuid:program_id>/edit/', views.edit_program, name='edit_program'),
    path('<uuid:program_id>/delete/', views.delete_program, name='delete_program'),
    path('<uuid:program_id>/enroll/', views.enroll, name='enroll'),
    
    # Program type specific views
    path('regular-english/', views.regular_english, name='regular_english'),
    path('plus-english/', views.plus_english, name='plus_english'),
    path('test-prep/ielts/', views.ielts, name='ielts'),
    path('test-prep/toefl/', views.toefl, name='toefl'),
    path('business-english/', views.business_english, name='business_english'),
    path('esp/', views.esp, name='esp'),
    path('eap/', views.eap, name='eap'),
    path('non-english/', views.non_english, name='non_english'),
] 
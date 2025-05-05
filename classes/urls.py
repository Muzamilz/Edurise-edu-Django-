from django.urls import path
from . import views

app_name = 'classes'

urlpatterns = [
    path('', views.class_list, name='class_list'),
    path('create/', views.create_class, name='create_class'),
    path('<uuid:class_id>/', views.class_detail, name='class_detail'),
    path('<uuid:class_id>/attendance/', views.track_attendance, name='track_attendance'),
    path('<uuid:class_id>/feedback/', views.submit_feedback, name='submit_feedback'),
    path('calendar/', views.calendar_view, name='calendar'),
] 
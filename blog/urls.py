from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Public URLs
    path('', views.blog_list, name='blog_list'),
    path('post/<slug:slug>/', views.blog_detail, name='blog_detail'),
    
    # Admin URLs
    path('create/', views.create_post, name='create_post'),
    path('post/<slug:slug>/edit/', views.edit_post, name='edit_post'),
    path('post/<slug:slug>/delete/', views.delete_post, name='delete_post'),
    path('posts/', views.post_list, name='post_list'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.create_category, name='create_category'),
    path('categories/<slug:slug>/edit/', views.edit_category, name='edit_category'),
    path('categories/<slug:slug>/delete/', views.delete_category, name='delete_category'),
    path('comments/', views.comment_list, name='comment_list'),
    path('comment/<uuid:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('comment/<uuid:comment_id>/approve/', views.approve_comment, name='approve_comment'),
]

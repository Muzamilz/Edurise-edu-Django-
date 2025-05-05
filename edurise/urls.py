"""
URL configuration for edurise project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    # Use custom admin dashboard instead of Django admin
    path('admin/', lambda request: redirect('admin_tools:dashboard'), name='admin_redirect'),
    path('admin_tools/', include('admin_tools.urls', namespace='admin_tools')),
    path('auth/', include('authentication.urls', namespace='auth')),
    path('programs/', include('programs.urls', namespace='programs')),
    path('enrollments/', include('enrollments.urls', namespace='enrollments')),
    path('classes/', include('classes.urls', namespace='classes')),
    path('profiles/', include('profiles.urls', namespace='profiles')),
    path('blog/', include('blog.urls', namespace='blog')),
    path('zoom/', include('zoom_integration.urls', namespace='zoom')),
    # path('testimonials/', include('testimonials.urls', namespace='testimonials')),  # Temporarily commented out
    path('', lambda request: redirect('auth:home'), name='root'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

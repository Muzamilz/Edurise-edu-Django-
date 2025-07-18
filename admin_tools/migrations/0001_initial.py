# Generated by Django 5.2 on 2025-05-01 22:47

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SystemHealthLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cpu_usage', models.FloatField()),
                ('memory_usage', models.FloatField()),
                ('disk_usage', models.FloatField()),
                ('database_queries', models.IntegerField()),
                ('response_time', models.FloatField()),
                ('error_count', models.IntegerField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'System Health Log',
                'verbose_name_plural': 'System Health Logs',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='AnalyticsReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('report_type', models.CharField(choices=[('user_growth', 'User Growth'), ('course_performance', 'Course Performance'), ('revenue', 'Revenue'), ('engagement', 'User Engagement'), ('custom', 'Custom Report')], max_length=50)),
                ('parameters', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_run', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Analytics Report',
                'verbose_name_plural': 'Analytics Reports',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='AnalyticsData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.JSONField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='data_points', to='admin_tools.analyticsreport')),
            ],
            options={
                'verbose_name': 'Analytics Data',
                'verbose_name_plural': 'Analytics Data',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='APILog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('endpoint', models.CharField(max_length=255)),
                ('method', models.CharField(max_length=10)),
                ('status_code', models.IntegerField()),
                ('response_time', models.FloatField()),
                ('ip_address', models.GenericIPAddressField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'API Log',
                'verbose_name_plural': 'API Logs',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='ErrorLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.CharField(choices=[('debug', 'Debug'), ('info', 'Info'), ('warning', 'Warning'), ('error', 'Error'), ('critical', 'Critical')], max_length=10)),
                ('message', models.TextField()),
                ('stack_trace', models.TextField(blank=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Error Log',
                'verbose_name_plural': 'Error Logs',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='UserActivityLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('login', 'Login'), ('logout', 'Logout'), ('profile_update', 'Profile Update'), ('password_change', 'Password Change'), ('role_change', 'Role Change'), ('permission_change', 'Permission Change'), ('enrollment', 'Enrollment'), ('course_access', 'Course Access'), ('content_access', 'Content Access'), ('report_generation', 'Report Generation')], max_length=50)),
                ('details', models.TextField(blank=True)),
                ('ip_address', models.GenericIPAddressField()),
                ('user_agent', models.TextField(blank=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activity_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Activity Log',
                'verbose_name_plural': 'User Activity Logs',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='UserSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(max_length=40, unique=True)),
                ('ip_address', models.GenericIPAddressField()),
                ('user_agent', models.TextField(blank=True)),
                ('last_activity', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sessions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Session',
                'verbose_name_plural': 'User Sessions',
                'ordering': ['-last_activity'],
            },
        ),
        migrations.CreateModel(
            name='UserPermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('permission_name', models.CharField(choices=[('can_manage_users', 'Can Manage Users'), ('can_manage_courses', 'Can Manage Courses'), ('can_manage_enrollments', 'Can Manage Enrollments'), ('can_view_reports', 'Can View Reports'), ('can_manage_settings', 'Can Manage Settings'), ('can_manage_content', 'Can Manage Content'), ('can_manage_analytics', 'Can Manage Analytics'), ('can_manage_system', 'Can Manage System')], max_length=50)),
                ('granted_at', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('granted_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='granted_permissions', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='permissions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Permission',
                'verbose_name_plural': 'User Permissions',
                'unique_together': {('user', 'permission_name')},
            },
        ),
    ]

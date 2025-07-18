# Generated by Django 5.2 on 2025-05-01 22:34

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('classes', '0001_initial'),
        ('programs', '0002_educationalprogram_default_meeting_duration_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MeetingTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('topic', models.CharField(max_length=255)),
                ('duration', models.IntegerField(help_text='Duration in minutes')),
                ('settings', models.JSONField(default=dict, help_text='Zoom meeting settings')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='zoom_meeting_templates', to='programs.educationalprogram')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meeting_templates', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='BulkMeetingSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('days_of_week', models.JSONField(help_text='List of days (0-6, where 0 is Monday)')),
                ('time_slots', models.JSONField(help_text='List of time slots in HH:MM format')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bulk_schedules', to='programs.educationalprogram')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bulk_schedules', to=settings.AUTH_USER_MODEL)),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='zoom_integration.meetingtemplate')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ZoomMeeting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic', models.CharField(max_length=200)),
                ('start_time', models.DateTimeField()),
                ('duration', models.IntegerField(help_text='Duration in minutes')),
                ('zoom_meeting_id', models.CharField(max_length=100)),
                ('join_url', models.URLField()),
                ('is_recurring', models.BooleanField(default=False)),
                ('recurrence_pattern', models.JSONField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('feedback_enabled', models.BooleanField(default=True)),
                ('bulk_schedule', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='zoom_integration.bulkmeetingschedule')),
                ('class_instance', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='zoom_meetings', to='classes.class')),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='zoom_meetings', to='programs.educationalprogram')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='zoom_meetings', to=settings.AUTH_USER_MODEL)),
                ('template', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='zoom_integration.meetingtemplate')),
            ],
            options={
                'ordering': ['-start_time'],
            },
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('file', models.FileField(upload_to='meeting_resources/')),
                ('category', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('uploaded_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='zoom_resources', to=settings.AUTH_USER_MODEL)),
                ('meeting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='zoom_resources', to='zoom_integration.zoommeeting')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddField(
            model_name='bulkmeetingschedule',
            name='created_meetings',
            field=models.ManyToManyField(related_name='bulk_schedules', to='zoom_integration.zoommeeting'),
        ),
        migrations.CreateModel(
            name='ZoomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zoom_user_id', models.CharField(max_length=100)),
                ('access_token', models.TextField()),
                ('refresh_token', models.TextField()),
                ('token_expires_at', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ZoomAnalytics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('total_meetings', models.IntegerField(default=0)),
                ('total_participants', models.IntegerField(default=0)),
                ('average_duration', models.IntegerField(default=0)),
                ('total_attendance', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='zoom_analytics', to='programs.educationalprogram')),
            ],
            options={
                'unique_together': {('program', 'date')},
            },
        ),
        migrations.CreateModel(
            name='ZoomAttendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('join_time', models.DateTimeField()),
                ('leave_time', models.DateTimeField(blank=True, null=True)),
                ('duration', models.IntegerField(blank=True, help_text='Duration in minutes', null=True)),
                ('status', models.CharField(choices=[('present', 'Present'), ('late', 'Late'), ('absent', 'Absent'), ('excused', 'Excused')], max_length=20)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='zoom_attendance', to=settings.AUTH_USER_MODEL)),
                ('meeting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance', to='zoom_integration.zoommeeting')),
            ],
            options={
                'unique_together': {('meeting', 'student')},
            },
        ),
        migrations.CreateModel(
            name='MeetingFeedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])),
                ('comment', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('meeting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedback', to='zoom_integration.zoommeeting')),
            ],
            options={
                'ordering': ['-created_at'],
                'unique_together': {('meeting', 'student')},
            },
        ),
    ]

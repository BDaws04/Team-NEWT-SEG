# Generated by Django 5.1.2 on 2024-11-24 23:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutorials', '0006_session_frequency'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tutor',
            name='hourly_rate',
        ),
        migrations.AddField(
            model_name='student',
            name='previous_sessions',
            field=models.ManyToManyField(blank=True, related_name='students_taken', to='tutorials.session'),
        ),
    ]
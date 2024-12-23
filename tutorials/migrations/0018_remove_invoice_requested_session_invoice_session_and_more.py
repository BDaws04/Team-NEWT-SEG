# Generated by Django 5.1.2 on 2024-12-09 22:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutorials', '0017_merge_20241206_1427'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='requested_session',
        ),
        migrations.AddField(
            model_name='invoice',
            name='session',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to='tutorials.studentsession'),
        ),
        migrations.AddField(
            model_name='studentsession',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Cancelled', 'Cancelled')], default='Pending', max_length=20),
        ),
    ]

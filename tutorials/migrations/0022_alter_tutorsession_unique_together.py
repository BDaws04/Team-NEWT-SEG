# Generated by Django 5.1.2 on 2024-12-11 19:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tutorials', '0021_alter_invoice_amount_alter_invoice_due_date_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='tutorsession',
            unique_together={('tutor', 'session')},
        ),
    ]
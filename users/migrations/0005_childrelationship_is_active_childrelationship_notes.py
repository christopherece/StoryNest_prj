# Generated by Django 5.2.1 on 2025-06-02 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_remove_profile_parent'),
    ]

    operations = [
        migrations.AddField(
            model_name='childrelationship',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='childrelationship',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
    ]

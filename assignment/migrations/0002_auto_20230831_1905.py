# Generated by Django 3.2.14 on 2023-08-31 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assignment', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assignment',
            name='content',
        ),
        migrations.RemoveField(
            model_name='assignment',
            name='title',
        ),
        migrations.AddField(
            model_name='assignment',
            name='assignment_description',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='assignment',
            name='assignment_title',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='assignment',
            name='assignment_type',
            field=models.CharField(choices=[('essay', 'Essay'), ('presentation', 'Presentation')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='assignment',
            name='has_ai_component',
            field=models.BooleanField(null=True),
        ),
        migrations.AddField(
            model_name='assignment',
            name='is_collaborative',
            field=models.BooleanField(null=True),
        ),
        migrations.AddField(
            model_name='assignment',
            name='learning_objectives',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='assignment',
            name='percent_of_cheating_students',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='assignment',
            name='subject',
            field=models.CharField(choices=[('english', 'English'), ('history', 'History')], max_length=20, null=True),
        ),
    ]

# Generated by Django 2.2.7 on 2019-12-19 23:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lecture',
            name='slug',
        ),
    ]

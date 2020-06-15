# Generated by Django 3.0.6 on 2020-06-15 10:08

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('slug', models.CharField(max_length=255)),
                ('subtitle', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('image', models.ImageField(upload_to='course_images')),
                ('vimeo_promo_video_id', models.CharField(max_length=50)),
                ('release_date', models.DateField()),
                ('download_link', models.URLField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('number', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.Course')),
            ],
        ),
        migrations.CreateModel(
            name='Lecture',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('vimeo_video_id', models.CharField(blank=True, max_length=50)),
                ('number', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('text', models.TextField(blank=True)),
                ('preview', models.BooleanField(default=False)),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.Section')),
            ],
        ),
        migrations.AddField(
            model_name='course',
            name='first_lecture',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='courses.Lecture'),
        ),
    ]

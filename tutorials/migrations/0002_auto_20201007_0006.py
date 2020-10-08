# Generated by Django 3.1.1 on 2020-10-07 00:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutorials', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutorial',
            name='status',
            field=models.CharField(choices=[('P', 'Published'), ('D', 'Draft')], default='D', max_length=3),
        ),
    ]
# Generated by Django 3.1.1 on 2020-12-07 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('money', '0006_auto_20200724_2352'),
    ]

    operations = [
        migrations.AddField(
            model_name='month',
            name='mrr',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]

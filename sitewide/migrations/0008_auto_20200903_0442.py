# Generated by Django 3.1.1 on 2020-09-03 04:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitewide', '0007_zappyuser_apple_receipt'),
    ]

    operations = [
        migrations.AddField(
            model_name='zappyuser',
            name='paypal_subscription_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='zappyuser',
            name='first_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='first name'),
        ),
        migrations.AlterField(
            model_name='zappyuser',
            name='stripe_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='zappyuser',
            name='stripe_subscription_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]

from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime, timedelta

class ZappyUser(AbstractUser):

    stripe_id = models.CharField(max_length=255)
    stripe_subscription_id = models.CharField(max_length=255)
    cancel_at_period_end = models.BooleanField(default=False)
    active_membership = models.BooleanField(default=False)

    # I think the only reason we do this is to have something in the model?
    def __str__(self):
        return self.email


class InviteKeys(models.Model):
    key = models.CharField(max_length=256)
    invite_password = models.CharField(max_length=512, null=True)
    email = models.EmailField(default='fun_coding@zappycode.com')
    code_expiration = models.DateField(default=datetime.now() + timedelta(days=14))
    membership_until = models.DateField(default=datetime.now() + timedelta(days=14))
    active = models.BooleanField(default=True)
    creator = models.CharField(max_length=128, default="ZappyCode")

    def __str__(self):
        return self.active

    def renew_key(self, user, days):
        find_key = self.objects.get(made_by__username=user)
        find_key.active = True
        new_expiration_date = datetime.now() + timedelta(days=days)
        find_key.code_expiration  = new_expiration_date
        find_key.save()
        self.save()


    def deactivate_key(self, key):
        to_deactivate = self.objects.get(key=key)
        to_deactivate.active = False
        to_deactivate.save()


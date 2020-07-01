from django.db import models
from django.contrib.auth.models import AbstractUser


class ZappyUser(AbstractUser):
    stripe_id = models.CharField(max_length=255)
    stripe_subscription_id = models.CharField(max_length=255)
    cancel_at_period_end = models.BooleanField(default=False)
    active_membership = models.BooleanField(default=False)
    pic = models.ImageField(upload_to='sitewide/user_pics', null=True)

    # I think the only reason we do this is to have something in the model?
    def __str__(self):
        return self.email

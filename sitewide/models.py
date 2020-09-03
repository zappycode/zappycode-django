from django.db import models
from django.contrib.auth.models import AbstractUser


class ZappyUser(AbstractUser):
    stripe_id = models.CharField(max_length=255, null=True, blank=True)
    stripe_subscription_id = models.CharField(max_length=255, null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)
    apple_product_id = models.CharField(max_length=255, blank=True, null=True)
    apple_expires_date = models.DateField(blank=True, null=True)
    apple_receipt = models.TextField(blank=True, null=True)
    active_membership = models.BooleanField(default=False)
    pic = models.ImageField(upload_to='sitewide/user_pics', null=True, blank=True)
    paypal_subscription_id = models.CharField(max_length=255, null=True, blank=True)

    # I think the only reason we do this is to have something in the model?
    def __str__(self):
        return self.email


# model is needed because of case not getting data from github API
class LastCommit(models.Model):
    commit_url = models.URLField()
    commit_time = models.DateTimeField()
    last_checked = models.DateTimeField()

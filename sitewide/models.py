from datetime import datetime
from paypalrestsdk import BillingAgreement, ResourceNotFound
from django.db import models
from django.contrib.auth.models import AbstractUser
import stripe
from stripe.error import InvalidRequestError
import environ
import courses.models

env = environ.Env()
environ.Env.read_env()
stripe.api_key = env.str('STRIPE_API_KEY')


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

    def check_stripe(self):
        try:
            subscription = stripe.Subscription.retrieve(self.stripe_subscription_id)
            status = (subscription['status'].lower(), datetime.fromtimestamp(int(subscription['current_period_end'])))
        except InvalidRequestError:
            status = None
        return status

    def check_paypal(self):
        try:
            subscription = BillingAgreement.find(self.paypal_subscription_id)
            if subscription.state.lower() != "suspended":
                end_date = subscription.agreement_details.next_billing_date
            else:
                end_date = subscription.agreement_details.last_payment_date
            # to be sure no errors with strptime method
            if end_date:
                end_date = datetime.strptime(end_date,  "%Y-%m-%dT%H:%M:%SZ")
            status = (subscription.state.lower(), end_date)
        except ResourceNotFound:
            status = None
        return status

    def user_history_courses(self):
        __courses = courses.models.Course.objects.filter(userhistory__user=self.id).order_by('title')
        return __courses

    def get_lectures_from_id(self):
        __lecture_link = courses.models.Lecture.objects.filter(userhistory__user=self.id)
        return __lecture_link


# model for archive reasons of subscription cancellations
class CancellationReasons(models.Model):
    user = models.ForeignKey(ZappyUser, on_delete=models.DO_NOTHING)
    membership_type = models.CharField(max_length=32, null=True, blank=True)
    reason = models.TextField(null=True, blank=True)


# model is needed because of case not getting data from github API
class LastCommit(models.Model):
    commit_url = models.URLField()
    commit_time = models.DateTimeField()
    last_checked = models.DateTimeField()


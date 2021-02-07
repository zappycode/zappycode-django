from allauth.account.forms import SignupForm
from django.forms import ModelForm
import stripe
from django.conf import settings
import environ
from django import forms
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import pluralize

from invites.models import Invite
from sitewide.models import ZappyUser, PaymentPlan

env = environ.Env()
environ.Env.read_env()


class StripeObj:
    payment_method = None
    customer = None
    subscription = None

    def __init__(self, stripe_token, email, plan):
        self.__set_payment_method(stripe_token=stripe_token)
        self.__set_stripe_customer(email=email)
        self.__set_stripe_subscription(plan=plan)

    def __set_payment_method(self, stripe_token):
        self.payment_method = stripe.PaymentMethod.create(
            type='card',
            card={'token': stripe_token}
        )

    def __set_stripe_customer(self, email):
        self.customer = stripe.Customer.create(
            payment_method=self.payment_method,
            email=email,
            invoice_settings={'default_payment_method': self.payment_method},
        )

    def __set_stripe_subscription(self, plan):
        self.subscription = stripe.Subscription.create(
            customer=self.customer.id,
            items=[{'plan': plan}, ],
            expand=['latest_invoice.payment_intent'],
        )


class CustomSignupForm(SignupForm):
    def signup_dispatcher(self, request):
        if 'invite' in request.POST:
            return self.invite_signup(request)

        elif 'paypalID' in request.POST:
            return self.paypal_signup(request)

        else:
            return self.default_signup(request)

    def signup_user(self, request, *args, **kwargs):
        user = super(CustomSignupForm, self).save(request)
        # Not 100% sure if this will work. It should.
        # Check that: https://stackoverflow.com/a/4112311
        user.update(**kwargs)

        return user

    def invite_signup(self, request):
        invite = get_object_or_404(Invite, token=request.POST['invite'])

        # I do always try to have a flat codebase.
        # If a function should return a value it should end by returning sth.
        # not by raising an error
        #
        # is_valid is new added property to model
        if not invite.is_valid or not request.user.is_anonymous:
            raise forms.ValidationError('Something went really wrong fam')

        user = self.signup_user(active_membership=True)
        invite.receiver = user
        invite.save()

        success_message = (
            'You now have free access to ZappyCode for the next '
            f'{invite.days_left()} day{pluralize(invite.days_left())}!'
        )
        messages.success(request, success_message)
        return user

    def paypal_signup(self, request):
        # Exception is removed here. It's removed, because it was tried
        # to catch any Error. This should be done at entry point of that form
        # instead of in a specific method. On Top:
        # No external API is in used. except
        # `super(CustomSignupForm, self).save(request)` there is no reason why
        # that code could fail.

        if not request.user.is_anonymous:
            raise forms.ValidationError('Something went really wrong fam')

        user = self.signup_user(
            active_membership=True,
            paypal_subscription_id=request.POST['paypalID']
        )

        success_message = 'Yes, yes, yes pal. You\'re now a part of ZappyCode!'
        messages.success(request, success_message)
        return user

    def default_signup(self, request):
        stripe.api_key = env.str('STRIPE_API_KEY', default='')

        # What about user.is_anonymous check here?

        plan_identifier = request.GET.get('plan', None)
        if not plan_identifier or settings.DEBUG:
            # Note: Database must include monthly25 already
            plan_identifier = "monthly25"
        plan = PaymentPlan.objects.get(_id=plan_identifier).displayed_plan

        # What if stripeToken is None?
        stripe_token = request.POST.get('stripeToken')
        email = self.cleaned_data.get("email")
        stripe_obj = StripeObj(
            stripe_token=stripe_token,
            email=email,
            plan=plan
        )

        user = self.signup_user(
            active_membership=True,
            stripe_subscription_id=stripe_obj.subscription.stripe_id,
            stripe_id=stripe_obj.customer.stripe_id
        )

        return user

    def save(self, request):
        try:
            return self.signup_dispatcher(request)
        except Exception as e:
            raise forms.ValidationError(e)


class AccountSettingsForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        # erase label from pic, set no validation on hidden pic input
        self.fields['pic'].label = ''
        self.fields['pic'].required = False

    class Meta:
        model = ZappyUser
        fields = ['pic']

        # ImageField is switched to display none.
        # Purpose: styling of FileInput's button is impossible.
        # But there is possibility of styling related label
        # which is made in account.html file
        widgets = {
            'pic': forms.ClearableFileInput(
                attrs={
                    'style': "display: none",
                },
            ),
        }

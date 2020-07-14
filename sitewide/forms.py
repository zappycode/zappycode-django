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
from sitewide.models import ZappyUser

env = environ.Env()
environ.Env.read_env()


class CustomSignupForm(SignupForm):

    def save(self, request):
        if 'invite' in request.POST:
            invite = get_object_or_404(Invite, token=request.POST['invite'])
            if not invite.is_expired():
                if invite.receiver is None:
                    if request.user.is_anonymous:
                        user = super(CustomSignupForm, self).save(request)
                        invite.receiver = user
                        invite.save()
                        user.active_membership = True
                        user.save()
                        messages.success(request,
                                         f'You now have free access to ZappyCode for the next {invite.days_left()} day{pluralize(invite.days_left())}!')
                        return user
            raise forms.ValidationError('Something went really wrong fam')
        else:
            try:
                stripe.api_key = env.str('STRIPE_API_KEY', default='')

                switcher = {
                    'monthly5': 'plan_GghOjUAr4KMyA7',
                    'monthly10': 'plan_GghOSq4jRIpZSa',
                    'monthly15': 'plan_GghO8pPwbQSlSO',
                    'monthly20': 'plan_GghPEC2t636ZTz',
                    'monthly25': 'plan_G06TRlhuiS8QbS',
                    'monthly30': 'plan_GghPkjHYPWQjGu',
                    'monthly35': 'plan_GghPnOFTwsMFwT',
                    'monthly40': 'plan_GghPgGgVB6WSi9',
                    'monthly45': 'plan_GghPsSiT5yoLqK',
                    'yearly50': 'plan_GghTB9FbYkUlDd',
                    'yearly100': 'plan_GghTeRpcRrHyx9',
                    'yearly150': 'plan_GghTRG8PabXLAe',
                    'yearly200': 'plan_GghSv7fchXUyVv',
                    'yearly250': 'plan_GghS8i6yB5VdFu',
                    'yearly300': 'plan_GghSMGrFDapIBJ',
                    'yearly350': 'plan_GghSLi8Rxnz8z0',
                    'yearly400': 'plan_GghS8ujc5jv2Ri',
                    'yearly450': 'plan_GghRPuoPX2WrxY',
                }
                plan = switcher.get(request.GET.get('plan', ''), 'plan_G06TRlhuiS8QbS')  # Default is $25 monthly
                if settings.DEBUG:
                    plan = 'plan_FiKTpHFoE4oGhp'

                payment_method = stripe.PaymentMethod.create(
                    type='card',
                    card={
                        'token': request.POST.get('stripeToken'),
                    },
                )

                customer = stripe.Customer.create(
                    payment_method=payment_method,
                    email=self.cleaned_data.get("email"),
                    invoice_settings={
                        'default_payment_method': payment_method,
                    },
                )

                subscription = stripe.Subscription.create(
                    customer=customer.id,
                    items=[
                        {
                            'plan': plan,
                        },
                    ],
                    expand=['latest_invoice.payment_intent'],
                )
                user = super(CustomSignupForm, self).save(request)
                user.stripe_subscription_id = subscription.stripe_id
                user.active_membership = True
                user.stripe_id = customer.stripe_id
                user.save()
                return user

            except Exception as e:
                raise forms.ValidationError(e)


class AccountSettingsForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args,**kwargs)
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
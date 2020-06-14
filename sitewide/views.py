import time
import stripe
import uuid
from datetime import datetime, timedelta
from django.urls import reverse
from .models import ZappyUser
from django.views import View
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from courses.models import Course
from django.contrib import messages
import environ

from sitewide.models import InviteKeys
from sitewide.forms import InviteLinkForm

env = environ.Env()
environ.Env.read_env()


def home(request):
    courses = Course.objects.order_by('-release_date')[:3]
    return render(request, 'sitewide/home.html', {'courses': courses})


def pricing(request):
    return render(request, 'sitewide/pricing.html')


@login_required
def account(request):
    return render(request, 'account/account.html')


def checkout(request):
    if not request.user.is_authenticated:
        return redirect(reverse('account_signup') + '?next=/checkout/%3Fplan%3D' + request.GET.get('plan', 'monthly25'))

    else:
        # fixed membership check. if auth and not active membership then redirect. using request.user it's not
        # enough. request user has no direct access to ZappyUser fields
        try:
            z_user = ZappyUser.objects.get(pk=request.user.id)
            if z_user.active_membership:
                messages.warning(request, 'You already have a zappycode membership')
                return redirect('home')
        # as somewhere below hope it's value error. have to be checked. need to be something because against PEP8
        except ValueError:
            messages.error(request, "Oops! Something went wrong. Please try again" )
            redirect('pricing')

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

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        subscription_data={
            'items': [{
                'plan': plan,
            }],

        },
        customer_email=request.user.email,
        success_url='http://zappycode.com/payment_success?session_id={CHECKOUT_SESSION_ID}',
        cancel_url='http://zappycode.com/pricing',
    )

    return render(request, 'sitewide/checkout.html', {'session_id': session.stripe_id})


def payment_success(request):
    # Set your secret key: remember to change this to your live secret key in production
    # See your keys here: https://dashboard.stripe.com/account/apikeys

    events = stripe.Event.list(type='checkout.session.completed', created={
        # Check for events created in the last 24 hours.
        'gte': int(time.time() - 24 * 60 * 60),
    })

    for event in events.auto_paging_iter():
        session = event['data']['object']

        try:
            user = ZappyUser.objects.get(email=session['customer_email'])
            user.stripe_subscription_id = session['subscription']
            user.active_membership = True
            user.stripe_id = session['customer']
            user.save()

            messages.success(request, 'You\'re now a part of ZappyCode!')

        except:
            messages.error(request, 'Was unable to signup. Please contact support.')

    return redirect('home')


@login_required
def cancel_subscription(request):
    if request.method == 'POST':
        # fixed bindings to a user. this from request has no access to ZappyUser fields
        try:
            z_user = ZappyUser.objects.get(pk=request.user.id)
            subscription = stripe.Subscription.retrieve(z_user.stripe_subscription_id)
            subscription.cancel_at_period_end = True
            z_user.cancel_at_period_end = True
            subscription.save()
            request.z_user.save()

            messages.success(request, 'Your subscription has been canceled')
            return redirect('account')
        # hope it's value error. PEP8 shouting that without this except is to broad. but have to be checked
        except ValueError:
            messages.error(request, "Subscription has been NOT canceled. Try again, please.")
            redirect('account')

    return redirect('home')


class InviteGenerator(View):

    def get(self, request, *args, **kwargs):
        creator = get_object_or_404(ZappyUser, pk=request.user.id)

        if creator.is_staff:
            form = InviteLinkForm()
            cnx = {
                'code_expiration': datetime.now() + timedelta(days=14),
                'valid_until': datetime.now() + timedelta(days=30),
                'link': 'http://zappycode.com/invite/free?',
                'color': '#6e00ff',
                'form': form
            }

            return render(request, 'account/invite.html', cnx)
        else:
            messages.error(request, "Sorry! You don't have permission to get here")

        return redirect('home')

    def post(self, request, *args, **kwargs):
        invite_keys = InviteKeys()
        form = InviteLinkForm(request.POST)

        print(form.errors)
        print(str(request.user.username))

        # check whether it's valid:
        print(form.cleaned_data.items())
        if form.is_valid():
            # process the data in form.cleaned_data as required

            # invite_keys.expiration_date = datetime.now() - timedelta(days=form.cleaned_data['period'])
            invite_keys.membership_until = datetime.now() + timedelta(days=int(form.cleaned_data['period']))
            invite_keys.creator = request.user.username
            invite_keys.code_expiration = datetime.now() + timedelta(days=int(form.cleaned_data['code_expiration']))
            link = self.set_invitation_link()
            invite_keys.key = link
            invite_keys.save()

            # need to save first to fetch id of invite key. adding email to link. and again save
            invite_keys.key += invite_keys.email

            print(invite_keys.id)
            invite_keys.invite_password = self.key_make_password(invite_keys.creator, invite_keys.id)

            invite_keys.save()

            cnx = {
                'code_expiration': invite_keys.code_expiration,
                'valid_until': invite_keys.membership_until,
                'link': invite_keys.key,
                'form': form
            }

        else:
            cnx = {
                'error': form.errors,
                'form': form
            }

        return render(request, 'account/invite.html', cnx)

    # inner method and could be useful outside. just utility, no use of self
    @staticmethod
    def set_invitation_link(email='example@zappycode'):
        start_with = 'https://zappycode.com/invite/?'
        stamp = str(datetime.now().timestamp())
        uuit = str(uuid.uuid5(uuid.uuid1(), datetime.now().__str__()))
        key = stamp + '=ZaPPyCoDe=' + uuit + '=ZaPPyCoDe='
        return start_with + key

    # inner method and could be useful outside. just utility, no use of self
    @staticmethod
    def key_make_password(username, voucher_id):
        password = make_password(str(username) + str(voucher_id))
        return password
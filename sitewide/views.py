import time
import stripe
from django.urls import reverse
from .models import ZappyUser
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from courses.models import Course
from django.contrib import messages
import environ

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

    if request.user.active_membership:
        messages.warning(request, 'You already have a zappycode membership')
        return redirect('home')

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
        subscription = stripe.Subscription.retrieve(request.user.stripe_subscription_id)
        subscription.cancel_at_period_end = True
        request.user.cancel_at_period_end = True
        subscription.save()
        request.user.save()
        messages.success(request, 'Your subscription has been canceled')
        return redirect('account')

    return redirect('home')

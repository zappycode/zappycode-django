import time
import stripe

from .forms import AccountSettingsForm
from .models import ZappyUser
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from courses.models import Course
from django.contrib import messages
import environ

env = environ.Env()
environ.Env.read_env()

stripe.api_key = env.str('STRIPE_API_KEY', default='')


def home(request):
    courses = Course.objects.order_by('-release_date')[:3]
    return render(request, 'sitewide/home.html', {'courses': courses})


def pricing(request):
    return render(request, 'sitewide/pricing.html')


def newsletter(request):
    return render(request, 'sitewide/newsletter.html')


@login_required
def account(request):
    forms = AccountSettingsForm()
    if request.method == 'POST':
        user = request.user
        form = AccountSettingsForm(request.POST, request.FILES)

        if 'delete' in request.POST:
            user.pic.delete()
            messages.success(request, 'You\'ve deleted profile picture.')
        elif form.is_valid() and form.cleaned_data['pic']:
            user.pic = form.cleaned_data['pic']
            user.save()
            messages.success(request, 'Boom! You\'ve got new profile picture.')
            return redirect('/account/')
        else:
            messages.warning(request, 'You need to load picture to save it')
    return render(request, 'account/account.html', {'forms': forms})


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

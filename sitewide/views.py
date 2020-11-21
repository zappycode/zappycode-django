import time
import stripe

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from rest_framework.utils import json
from django.http import HttpResponse, JsonResponse
from .models import ZappyUser
from invites.models import Invite
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from courses.models import Course
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
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


def paypal(request):
    return render(request, 'sitewide/paypal.html')


# view for validate email and password with paypal smart button
def paypal_validation(request):
    if request.method == 'POST':
        # capture data sent from paypal.Buttons onClick
        to_validate = json.loads(request.body)

        # prepare dictionary to be sure there won't be empty json sent
        data = {'password_valid': True,
                'password_errors': None,
                'email_valid': True,
                'email_error': None,
                }
        try:
            # for password validation use validator django.core.validators
            validate_password(to_validate['password'])
            data['password_valid'] = True
            data['password_errors'] = None
        except ValidationError as e:
            data['password_valid'] = False
            data['password_errors'] = e.messages

        try:
            # for email validation use validator from django.core.validators
            validate_email(to_validate['email'])
            try:
                # if email has got proper format check if is already used
                ZappyUser.objects.get(email=to_validate['email'])
                data['email_valid'] = False
                data['email_error'] = 'Email address is already in use pal'
            except ObjectDoesNotExist:
                data['email_valid'] = True
                data['email_error'] = None
        except ValidationError:
            data['email_valid'] = False
            data['email_error'] = 'Enter a valid email address pal'
        # send result of validation to client in json format.
        # it gonna be captured in paypal.Buttons onClick
        return JsonResponse(data, safe=True)
    else:
        return render(request, 'sitewide/404.html')


def error404(request, exception):
    return render(request, 'sitewide/404.html')

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


@staff_member_required
def check_active_memberships(request):
    active_members = ZappyUser.objects.filter(active_membership=True)
    users_membership_expired = set()
    valid_membership = set()

    for user in active_members:
        # Invites
        for invite in Invite.objects.filter(receiver=user):
            if invite.is_expired():
                users_membership_expired.add(user)
            else:
                users_membership_expired.discard(user)
                valid_membership.add(user)
                break

        # Stripe
        if user.stripe_subscription_id:
            sub = stripe.Subscription.retrieve(user.stripe_subscription_id)
            if sub['status'] != 'canceled':
                valid_membership.add(user)
                users_membership_expired.discard(user)
            elif user not in valid_membership:
                users_membership_expired.add(user)

        # Paypal - Need to actually check if these are valid here :)
        if user.paypal_subscription_id:
            users_membership_expired.discard(user)
            valid_membership.add(user)

    for user in users_membership_expired:
        user.active_membership = False
        user.save()

    return HttpResponse(f"Done! {len(users_membership_expired)} user memberships canceled. " + ' '.join(map(str, users_membership_expired)))

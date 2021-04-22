import time
from datetime import datetime

import stripe
import environ
import json
import requests
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from paypalrestsdk import BillingAgreement
from rest_framework.utils import json
from django.http import HttpResponse, JsonResponse
from .forms import AccountSettingsForm
from .models import ZappyUser, CancellationReasons
from invites.models import Invite
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from courses.models import Course
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required

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


@login_required
def account(request):
    user = request.user
    membership_warning = True
    membership = {}

    if request.method == 'GET':
        forms = AccountSettingsForm()
        if user.apple_receipt:
            # try statement in case of apple_expires_date is None for some reason
            try:
                if user.apple_expires_date >= datetime.now():
                    membership = {
                        "type": "apple",
                        "apple_product_id": user.apple_product_id,
                        "expiration_date": user.apple_expires_date
                    }
                    membership_warning = None
            except TypeError:
                membership = {
                    "type": "apple",
                    "apple_product_id": "Apple In App Purchase",
                    "expiration_date": None
                }
                membership_warning = None

        if user.stripe_subscription_id and membership_warning:
            stripe_sub = user.check_stripe()

            if stripe_sub[0] == 'active':
                membership = {
                   "type": "stripe",
                   "expiration_date": stripe_sub[1]
                }
                membership_warning = None

        if user.paypal_subscription_id and membership_warning:
            paypal_sub = user.check_paypal()

            if paypal_sub[0] == "active" or (paypal_sub[0] == "cancelled" and paypal_sub[1] >= datetime.now()):
                membership = {
                     "type": "paypal",
                     "expiration_date": paypal_sub[1]
                }
                membership_warning = None

        if membership_warning:
            if Invite.has_invite(request.user):
                membership = {
                    "type": "invite",
                    "expiration_date": Invite.has_invite(request.user)
                }
                membership_warning = None
            else:
                message = "User " + request.user.username + ", email: " + request.user.email \
                          + " has got a corrupted membership. " \
                            "There is no valid subscription (active or cancelled) or invitation. "
                send_mail("Broken membership", message, env.str('ADMIN_EMAIL'),
                          [env.str('ADMIN_EMAIL')], fail_silently=False)
    else:
        form = AccountSettingsForm(request.POST, request.FILES)
        if 'delete' in request.POST:
            user.pic.delete()
            messages.success(request, 'You\'ve deleted profile picture.')
        elif form.is_valid() and form.cleaned_data['pic']:
            user.pic = form.cleaned_data['pic']
            user.save()
            messages.success(request, 'Boom! You\'ve got new profile picture.')
        else:
            messages.warning(request, 'You need to load picture to save it')
        return redirect('/account')

    return render(request, 'account/account.html', {
        'forms': forms, 'membership': membership, "membership_warning": membership_warning
    })


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
def cancel_subscription(request, membership):
    subject = ""
    message = ""
    reasons = ""
    if request.method == 'POST':
        # save reasons of cancellation to the db
        for reason in request.POST.getlist('reason'):
            if reason != 'Other':
                CancellationReasons(reason = reason, membership_type=membership, user=request.user).save()
                reasons += str(reason) + ", "
            else:
                CancellationReasons(reason=request.POST["other-reasons"], membership_type=membership, user=request.user).save()
                reasons += request.POST["other-reasons"]

        if membership == 'stripe':
            # modify used to hit API only once
            stripe.Subscription.modify(
                request.user.stripe_subscription_id,
                cancel_at_period_end=True,
            )
            request.user.cancel_at_period_end = True
            request.user.save()
            message = "I've cancelled subscription': " + str(request.user.stripe_subscription_id) + "\n"\
                      + "\n" + "Reasons: " + reasons
            subject = "Cancellation of Stripe subscription"
            messages.success(request, 'Your subscription has been canceled')
        elif membership == 'paypal':
            cancel_note = {"note": "Canceling the agreement"}
            if BillingAgreement.find(request.user.paypal_subscription_id).cancel(cancel_note):
                messages.success(request, 'Your subscription has been canceled')
                request.user.cancel_at_period_end = True
                request.user.save()
                message = "I've cancelled subscription': " + str(request.user.paypal_subscription_id) + "\n" \
                          + "\n" + "Reasons: " + reasons
                subject = "Cancellation of Paypal subscription"
            # send email with cancel request if automatic cancellation failed
            else:
                message = "I would like to cancel my subscription id: " + str(request.user.paypal_subscription_id) + "\n" \
                          + "Reasons: " + reasons
                subject = "Cancellation request of paypal subscription"
                messages.warning(request, 'Something went wrong. Your subscription has been not canceled. '
                                          'Email with cancellation request has been sent to ZappyCode')
        elif membership == 'apple':
            messages.success(request, 'Email with cancel request of your subscription '
                                      'has been successfully sent to ZappyCode. '
                                      'We cancel your subscription as soon as it\'s possible')
            message = "I would like to cancel my subscription id: " + str(request.user.apple_product_id) + "\n"\
                      + "Apple receipt: " + str(request.user.apple_receipt) + "\n" + "Reasons: " + reasons
            subject = "Cancellation request of Apple subscription"

        send_mail(subject, request.user.email + ' ' + message, env.str('ADMIN_EMAIL'), [env.str('ADMIN_EMAIL')], fail_silently=False)
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

def get_receipt_data(receipt):
    verify_url = 'https://buy.itunes.apple.com/verifyReceipt'
    
    receipt_json = json.dumps({"receipt-data": receipt, 'password': env.str('APP_SHARED_SECRET', default='')})
    response = requests.request(
        method='POST',
        url=verify_url,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data=receipt_json
    )
    
    res_json = response.json()
    
    if res_json['status'] == 21007:
        # Apple docs say try prod and if no dice, then do sandbox https://developer.apple.com/library/archive/technotes/tn2413/_index.html#//apple_ref/doc/uid/DTS40016228-CH1-RECEIPTURL
        response = requests.request(
            method='POST',
            url='https://sandbox.itunes.apple.com/verifyReceipt',
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data=receipt_json
        )

    res_json = response.json()
    
    return res_json
    
@user_passes_test(lambda u: u.is_superuser)
def apple_subscriptions(request):
    active_members = ZappyUser.objects.filter(active_membership=True)
    apple_members = []
    for user in active_members:
        print(user.email)
        if user.apple_receipt:
            receipt_json = get_receipt_data(user.apple_receipt)
            apple_members.append({'user' : user, 'receipt_json' : receipt_json})
            
    print(apple_members)
           
    return render(request, 'account/apple_subscriptions.html', {'apple_members' : apple_members}) 
    

import time
import stripe
import uuid
from operator import itemgetter
from datetime import datetime, timedelta
from django.utils.crypto import get_random_string
from allauth.account.views import login
from allauth.account.models import EmailAddress
from django.urls import reverse, resolve
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
from sitewide.overrided_auth_backend import NewRestrictionAuthenticationBackend as Validate_by_iKey

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
        # enough. request user has no direct access to ZappyUser fields. added validation users with access
        # from invitation linksdon't know if except is going to happen. in case murphy's law is true
        #  it will be better to use try. Cannot imagine more errors from 'try except'
        try:
            z_user = ZappyUser.objects.get(pk=request.user.id)
            if z_user.active_membership or Validate_by_iKey(z_user):
                messages.warning(request, 'You already have got a zappycode membership')
                return redirect('home')
            else:
                messages.warning(request, 'Your membership has expired. Grab new one')
                # !!!! user has got no membersip but got account, should be redirect to login!!!! don't know if working
                return redirect(reverse('pricing') + '?next=/checkout/%3Fplan%3D' + request.GET.get('plan', 'monthly25'))

        # hope it's right error. have to be checked. need to be something because against PEP8
        except AttributeError:
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

        # hope it's value error, can be as well AttributeError.
        # PEP8 shouting that without this except is to broad. but have to be checked
        except AttributeError:
            messages.error(request, "Subscription has been NOT canceled. Try again, please.")
            redirect('account')

    return redirect('home')


class InviteGenerator(View):

    def get(self, request, *args, **kwargs):
        creator = get_object_or_404(ZappyUser, pk=request.user.id)
        current_url = resolve(request.path).url_name
        print(current_url)
        print('Jestem w metodzie get InviteGenerator')
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

        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required

            invite_keys.membership_until = datetime.now() + timedelta(days=int(form.cleaned_data['period']))
            invite_keys.creator = request.user.username
            invite_keys.code_expiration = datetime.now() + timedelta(days=int(form.cleaned_data['code_expiration']))
            invite_keys.key = self.set_invitation_link((int(form.cleaned_data['period'])))
            invite_keys.save()

            # needed save first to fetch id of invite key. adding email to link. and again save
            invite_keys.key += invite_keys.email
            invite_keys.invite_password = self.key_make_password(invite_keys.creator, invite_keys.id)

            # zappy user binding
            invite_keys.key_owner = ZappyUser(
                username=invite_keys.key, password=invite_keys.invite_password
            ).save()

            invite_keys.save()

            cnx = {
                'e-mail': invite_keys.email,
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

    # inner method. just utility, no use of self
    @staticmethod
    def set_invitation_link(days=30, email=''):
        start_with = 'https://zappycode.com/invite/free?period='
        stamp = str(datetime.now().timestamp())
        uuit = str(uuid.uuid5(uuid.uuid1(), datetime.now().__str__()))
        key = str(days) + '&tmsp=' + stamp + '&ZaPPyCoDe=' + uuit + '&email=' + email
        return start_with + key

    @staticmethod
    def unzip_invitation_link(link):

        # http://127.0.0.1:8000/invite/free
        # ?period=62
        # &tmsp=1592409205.516944
        # &ZaPPyCoDe=fae08545-7e5b-5348-a84e-5b69ac7e245a
        # &email=fun_coding@zappycode.com

        # slicing link to return tuple of data
        key = link[link.find('?'):]
        period = link[link.find('=') + 1:link.find('&')]
        timestamp = link[link.find('&tmsp') + 6:link.find('&ZaPPyCoDe=')]
        email = link[link.rfind('=') + 1:]
        return key, period, email, timestamp

    # inner method. can be used in different class. just utility, no use of self
    # chain with default '' to make method more flexible to use.
    @staticmethod
    def key_make_password(chain='', *args):
        for arg in args:
            chain += str(arg)

        print(chain)
        print('jestem w key_make_password')
        return make_password(chain)


class InviteSignView(InviteGenerator):

    def __init__(self):
        super(InviteSignView, self).__init__()

        print(self.__dict__, 'jestem w __init__ InviteSignView')

    def get(self, request, *args, **kwargs):
        unpacked = self.unzip_invitation_link(request.get_full_path())

        print(unpacked)
        print('jesetem w get InviteSignView')

        if unpacked[2] != 'fun_coding@zappycode.com':
            #  feature to do- generate link with email address
            messages.error(request, 'Invitation link is incorrect')
            redirect('home')
        else:
            messages.error(request, "You have to sign up to activate your link")

            print('invite/free/' + unpacked[0], 'jesetem w w else metody get')

            return redirect(reverse('invite_signup', kwargs = request.GET), template_name='account/invite_signup.html')
        cnx = {
            'error': 'no w końcu się udało'
        }
        return render(request, 'account/invite_signup.html', cnx)



    def post(self, request, *args, **kwargs):
        if request.POST['password1'] == request.POST['password2']:

            try:
                user = ZappyUser.objects.get(email=request.POST['email'])
                return redirect(reverse(
                    'isignup' + request.get_full_path()[request.get_full_path().find('?'):],
                    {'error': 'User ' + str(user) + ' already exists!'},
                ))
            except AttributeError:
                user = ZappyUser.objects.get()
                # change email
                user.email = request.POST['email']
                # change password
                user.set_password(request.POST['password1'])
                # set active_membership
                user.active_membership = True
                user.save()

                # bindings to allauth emails
                EmailAddress(
                    user = user, email=user.email, primary=True, verified=True,
                ).save()

                # log in user and redirect home
                login(request, user)
                # and finally inform user about period of free access
                messages.success(request, 'Hurra! You have got free access to ZappyCode for ', self.unpacked[1],' days')

            return redirect('home')
        else:
            cnx = { 'error': 'Passwords not match!!!' }
            return redirect(reverse('invite_signup' + self.unpacked[0][self.unpacked[0].find('?'):], cnx))

    # method to be sure that password is really hashed
    @staticmethod
    def check_if_hashed(request, password):
        if password[:password.find('$')] != 'pbkdf2_sha256':
            messages.warning(request, 'For security reasons need to hash password')
            return InviteGenerator.key_make_password(password)
        return password

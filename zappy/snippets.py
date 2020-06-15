# overriding backend. allautch works with dajgo.auth. remember:
# in settings.py of your django project change AUTHENTICATION_BACKENDS = (
#
#     # Needed to login by username in Django admin, regardless of `allauth`
#     'django.contrib.auth.backends.ModelBackend',
#
#     # `allauth` specific authentication methods, such as login by e-mail
#     # 'allauth.account.auth_backends.AuthenticationBackend',
#
#     # switched on custom backend, uncommented default.
#     # source in sitewide/overrided_auth_backend.py
#     'sitewide.overrided_auth_backend.NewRestrictionAuthenticationBackend',
#
# )

from allauth.account.auth_backends import AuthenticationBackend
from django.contrib.auth.models import AbstractUser
from django.shortcuts import redirect, get_object_or_404
from sitewide.models import ZappyUser
from django.contrib import messages


# overriding authenticationBackend to have possibility to add new conditions.
# backend is added in settings.py insteadof default
class NewRestrictionAuthenticationBackend(AuthenticationBackend):
    # without this all features from parent class not going to work
    def __init__(self, *args, **kwargs):
        super(NewRestrictionAuthenticationBackend, self).__init__(*args, **kwargs)

    # override authenticate flow
    def authenticate(self, request, **credentials):

        # zappy is goin to keep all data about user
        zappy = ZappyUser(request, **credentials)

        try:
            # need again to call super() to collect all features of parent method.
            # but i could be wrong. need to test if can use just self.
            user = super().authenticate(request, **credentials)
            print(user.active_membership)
            if user.active_membership:
                return user
            else:
                messages.error(request, "Sorry! Your membership has expired")
                return None
        # one error raised for user in and not signed user
        except AttributeError:
            if ZappyUser.objects.filter(email=zappy.email).exists():
                messages.error(request, "Sorry! Your membership has expired")
            else:
                messages.error(request, "Sign up first to login")
        return None

    @staticmethod
    def check_email_in_db(email):
        return ZappyUser.objects.filter(email=email)
#
#    """So here we will see how to call a function using *args and **kwargs. Just consider that you have this little function:
#
# def test_args_kwargs(arg1, arg2, arg3):"""

def test_args_kwargs(arg1, arg2, arg3):
    print("arg1:", arg1)
    print("arg2:", arg2)
    print("arg3:", arg3)

# Now you can use *args or **kwargs to pass arguments to this little function. Here’s how to do it:

# first with *args
args = ("two", 3, 5)
test_args_kwargs(*args)
# output:
# arg1: two
# arg2: 3
# arg3: 5

# now with **kwargs:
kwargs = {"arg3": 3, "arg2": "two", "arg1": 5}
test_args_kwargs(**kwargs)

# output:
# arg1: 5
# arg2: two
# arg3: 3


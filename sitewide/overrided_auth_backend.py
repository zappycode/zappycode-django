from allauth.account.auth_backends import AuthenticationBackend
from django.contrib.auth.models import AbstractUser
from django.shortcuts import redirect, get_object_or_404
from .models import ZappyUser
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






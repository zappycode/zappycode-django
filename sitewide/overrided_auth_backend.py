from allauth.account.auth_backends import AuthenticationBackend
from django.contrib.auth.models import AbstractUser
from django.shortcuts import redirect, get_object_or_404
from .models import ZappyUser, InviteKeys
from django.contrib import messages
from datetime import datetime, timedelta


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

            # check_validity method works only with users from invitation links
            if self.check_validity(user) or user.active_membership:
                return user
            else:
                messages.error(request, "Sorry! Your membership has expired")
                return None

        # error is raised also for users which are in database. So
        except AttributeError:
            if ZappyUser.objects.filter(email=zappy.email).exists():
                messages.error(request, "Sorry! Your membership has expired")
            else:
                messages.error(request, "Sign up first to login")
        return None

    @staticmethod
    def check_validity(user):
        try:
            validator = InviteKeys.objects.get(pk=user.id)
            if datetime.now().date() <= validator.membership_until:
                return True
            else:
                # switch off active_membership (ZappyUser)
                validator.key_owner.active_membership = False
                return False
        except AttributeError:
            return False






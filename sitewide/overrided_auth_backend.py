from allauth.account.auth_backends import AuthenticationBackend
from django.contrib import messages


# overriding authenticationBackend to have possibility to add new conditions.
# backend is added in settings.py insteadof default
class NewRestrictionAuthenticationBackend(AuthenticationBackend):
    # without this all features from parent class not going to work
    def __init__(self, *args, **kwargs):
        super(NewRestrictionAuthenticationBackend, self).__init__(*args, **kwargs)

    # override authenticate flow
    def authenticate(self, request, **credentials):
        try:
            # need again to call super() to collect all features of parent method.
            # but i could be wrong. need to test if can use just self.
            user = super().authenticate(request, **credentials)
            print(user.active_membership)
            if user.active_membership:
                print('łoś')
                return user
            else:
                messages.error(request, "Sorry! Your membership has expired")
                return None
        except AttributeError:
            messages.error(request, "Oops! Check for possible typos")

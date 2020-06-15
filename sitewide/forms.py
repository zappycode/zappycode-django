from operator import itemgetter

from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms

from sitewide.models import ZappyUser


class ZappyUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = ZappyUser
        fields = ('username', 'email')


class ChangeZappyUserForm(UserChangeForm):
    class Meta:
        model = ZappyUser
        fields = ('username', 'email')


class InviteLinkForm(forms.Form):

    CODE_EXPIRATION = {
        (31, '1 month'),
        (21, '3 weeks'),
        (14, '2 weeks'),
        (7, '1 week'),
    }

    PERIOD = {
        (99, '3 months'),
        (62, '2 months'),
        (30, '1 month'),
        (14, '2 weeks'),
    }
    OPTIONS = {
        'e-mail': True,
    }


    code_expiration = forms.ChoiceField(widget=forms.RadioSelect(), initial={'value': 30}, choices=sorted(CODE_EXPIRATION, reverse=True))
    period = forms.ChoiceField(widget=forms.RadioSelect(), choices=sorted(PERIOD, key=itemgetter(0)))
    # valid_until = forms.DateField(widget=forms.DateInput(attrs={
    #         'class': 'form-control datepicker',
    #         'data-target': '#datepicker',
    # }))

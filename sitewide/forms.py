from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from sitewide.models import ZappyUser


class ZappyUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = ZappyUser
        fields = ('username', 'email')


class ChangeZappyUserForm(UserChangeForm):
    class Meta:
        model = ZappyUser
        fields = ('username', 'email')

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from sitewide.models import ZappyUser
from sitewide.forms import ZappyUserCreationForm, ChangeZappyUserForm


class ZappyUserAdmin(UserAdmin):
    add_form = ZappyUserCreationForm
    form = ChangeZappyUserForm
    model = ZappyUser
    list_display = ['email', 'username', 'stripe_id', 'active_membership', 'stripe_subscription_id']


admin.site.register(ZappyUser, ZappyUserAdmin)

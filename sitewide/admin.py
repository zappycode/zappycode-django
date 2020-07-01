from django.contrib import admin

from sitewide.models import ZappyUser


class ZappyUserAdmin(admin.ModelAdmin):
    model = ZappyUser
    list_display = ['email', 'username', 'stripe_id', 'active_membership', 'stripe_subscription_id', 'date_joined',
                    'last_login']


admin.site.register(ZappyUser, ZappyUserAdmin)

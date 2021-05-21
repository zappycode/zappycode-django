from django.contrib import admin

from sitewide.models import ZappyUser, CancellationReasons, LastCommit


class ZappyUserAdmin(admin.ModelAdmin):
    model = ZappyUser
    list_display = ['email', 'username', 'stripe_id', 'active_membership', 'stripe_subscription_id', 'date_joined',
                    'last_login']
                    
    search_fields = ['email','username']


admin.site.register(ZappyUser, ZappyUserAdmin)
admin.site.register(CancellationReasons)
admin.site.register(LastCommit)

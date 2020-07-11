from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Invite


class InviteAdmin(admin.ModelAdmin):
    list_display = ['token', 'link']

    def link(self, obj):
        if obj.sender:
            return mark_safe(f'<a href="{obj.get_absolute_url()}">{obj.sender.username} - {obj.token}</a>')
        else:
            return mark_safe(f'<a href="{obj.get_absolute_url()}">No Sender - {obj.token}</a>')


admin.site.register(Invite, InviteAdmin)

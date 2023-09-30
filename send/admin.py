from django.contrib import admin
from .models import SendIt
from django.utils.safestring import mark_safe

class SendAdmin(admin.ModelAdmin):
	list_display = ['name', 'link']

	def link(self, obj):
		return mark_safe(f'<a href="{obj.get_absolute_url()}">{obj}</a>')

admin.site.register(SendIt, SendAdmin)
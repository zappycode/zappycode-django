from django.contrib import admin
from .models import Post
from django.utils.safestring import mark_safe


class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'link']

    def link(self, obj):
        return mark_safe(f'<a href="{obj.get_absolute_url()}">Link</a>')


admin.site.register(Post, ProductAdmin)

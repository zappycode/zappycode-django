from django.contrib import admin
from .models import Post, Image
from django.utils.safestring import mark_safe


class ImageInline(admin.StackedInline):
    model = Image


class ProductAdmin(admin.ModelAdmin):
    inlines = [ImageInline]
    list_display = ['title', 'link']

    def link(self, obj):
        return mark_safe(f'<a href="{obj.get_absolute_url()}">Link</a>')


admin.site.register(Post, ProductAdmin)

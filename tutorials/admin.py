from django.contrib import admin
from .models import Tutorial

@admin.register(Tutorial)
class TutorialAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published', 'status',)
    list_filter = ('status', 'created', 'published', 'author')
    prepopulated_fields = {'slug':('title',)}
   

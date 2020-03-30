from django.contrib import admin
from .models import Course, Section, Lecture

admin.site.register(Course)
admin.site.register(Section)
admin.site.register(Lecture)

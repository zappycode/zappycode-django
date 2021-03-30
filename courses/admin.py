from django.contrib import admin
from .models import Course, Section, Lecture

class CourseAdmin(admin.ModelAdmin):
	model = Course
	raw_id_fields = ['first_lecture']

admin.site.register(Course, CourseAdmin)
admin.site.register(Section)
admin.site.register(Lecture)

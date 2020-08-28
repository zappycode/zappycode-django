from django.urls import path
from . import views

urlpatterns = [
    path('/lecture/<int:lecture_id>/download', views.download_video, name='download'),
    path('/<slug:course_slug>/<int:lecturepk>/<slug:lecture_slug>', views.view_lecture, name='view_lecture'),
    path('/<slug:course_slug>', views.course_landing_page, name='course_landing_page'),
    path('', views.all_courses, name='all_courses'),
]

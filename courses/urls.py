from django.urls import path

from . import views

urlpatterns = [
    # below path is for aproach with just passing lecture.preview = True without necessity of creating
    # html and something like that. crucial is to put path above rest of lecture path's.
    # needed to comment because to paths not work :)

    # path('<slug:course_slug>/<int:lecturepk>/<slug:lecture_slug><int:access>', views.view_lecture4all),

    # this path is for second approach just to show possibility of changing html and power of django blocks.
    # this approach need to have got own html which extending view_lecture.html
    path('<slug:course_slug>/<int:lecturepk>/<slug:lecture_slug><int:access>', views.view_lecture4all_second, name='view_lecture_4all'),

    path('<slug:course_slug>/<int:lecturepk>/<slug:lecture_slug>', views.view_lecture, name='view_lecture'),
    path('<slug:course_slug>', views.course_landing_page, name='course_landing_page'),
    path('', views.all_courses, name='all_courses'),


]



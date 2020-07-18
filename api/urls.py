from django.urls import path
import courses.views
from . import views

urlpatterns = [
    path('/courses', courses.views.CourseList.as_view()),
    path('/iap/signup', views.iap_signup),
]

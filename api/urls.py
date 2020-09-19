from django.urls import path
from . import views

urlpatterns = [
    path('/courses', views.CourseList.as_view()),
    path('/courses/<int:pk>', views.CourseWithSectionsAndLectures.as_view()),
    path('/iap/signup', views.iap_signup),
    path('/login', views.login),
]

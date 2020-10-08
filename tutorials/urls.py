from django.urls import path
from .views import TutorialListView, TutorialDetailView

app_name = "tutorials"

urlpatterns = [
    path('', TutorialListView.as_view(), name="tutorials_list"),
    path('/<str:slug>', TutorialDetailView.as_view(), name="tutorials_detail"),
]
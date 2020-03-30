from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('<int:post_pk>/<slug:post_slug>', views.view_post, name='view_post'),
]

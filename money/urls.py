from django.urls import path
from . import views

app_name = 'money'

urlpatterns = [
    path('<int:month_pk>/<slug:month_slug>/', views.view_month, name='view_month'),
    path('', views.home, name='home'),
]

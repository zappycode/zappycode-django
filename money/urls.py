from django.urls import path
from . import views
from .views import Paypal

app_name = 'money'

urlpatterns = [
    path('/<int:month_pk>/<slug:month_slug>/', views.view_month, name='view_month'),
    path('', views.home, name='home'),
    path('/paypal', Paypal.as_view(), name='paypal_mrr'),
]

from django.urls import path
from . import views

app_name = 'send'

urlpatterns = [
	path('/<uuid:redirect_uuid>/', views.sendit, name='sendit'),
]

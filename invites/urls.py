from django.urls import path
from . import views

app_name = 'invites'

urlpatterns = [
    path('/<uuid:token>', views.invite_landing_page, name='invite_landing_page'),
    path('/<uuid:token>/redeem', views.redeem_invite_to_existing_account, name='redeem_invite_to_existing_account'),
]

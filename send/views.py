from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from send.models import SendIt

# Create your views here.

def sendit(request, redirect_uuid):
	sendIt = get_object_or_404(SendIt, uuid=redirect_uuid)
	return redirect(sendIt.url)

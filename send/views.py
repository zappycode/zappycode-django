from django.shortcuts import redirect

# Create your views here.

def sendit(request, redirect_uuid):
	print(redirect_uuid)
	return redirect("http://stackoverflow.com/")

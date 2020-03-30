from django.shortcuts import render, get_object_or_404
from .models import Challenge

def challenge(request, pk):
    challenge = get_object_or_404(Challenge, pk=pk)
    return render(request, 'challenge/challenge.html', {'challenge':challenge})
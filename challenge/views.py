from django.shortcuts import render, get_object_or_404
from .models import Challenge
from courses.models import Course

def challenge(request, pk):
    challenge = get_object_or_404(Challenge, pk=pk)
    courses = Course.objects.filter(tags__name__in=challenge.tags.names()).distinct()
    return render(request, 'challenge/challenge.html', {'challenge':challenge, 'courses':courses})
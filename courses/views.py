from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from .models import Lecture, Section, Course
from sitewide.models import ZappyUser

import requests
from django.contrib import messages


@login_required
def download_video(request, lecture_id):
    lecture = get_object_or_404(Lecture, pk=lecture_id)
    user = ZappyUser.objects.get(email=request.user.email)
    if not lecture.download_url:
        lecture.get_download_url()

    # checking user permissions in case of open download url
    # outside of download button
    if user.active_membership:
        file_name = str(lecture.vimeo_video_id) + '.mp4'
        req = requests.get(lecture.download_url, stream=True, timeout=(5, 10))
        if req.status_code == 200:
            response = HttpResponse(req, content_type='video/mp4')
            response['Content-Disposition'] = 'attachment; filename=' + str(file_name)
            return response
        else:
            messages.warning(request, 'Bummer! Your download has failed')
            return render(request, 'courses/view_lecture.html', {'lecture': lecture})


def view_lecture(request, course_slug, lecturepk, lecture_slug):
    lecture = get_object_or_404(Lecture, pk=lecturepk)
    if not lecture.thumbnail_url:
        lecture.thumbnail_url = lecture.get_thumbnail_url()
        lecture.save()
    return render(request, 'courses/view_lecture.html', {'lecture': lecture})


def course_landing_page(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    return render(request, 'courses/course_landing_page.html', {'course': course})


def all_courses(request):
    courses = Course.objects.filter(published=True).order_by('-release_date')
    return render(request, 'courses/all_courses.html', {'courses': courses})

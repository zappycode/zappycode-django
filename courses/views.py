from django.shortcuts import render, get_object_or_404
from .models import Lecture, Section, Course
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def view_lecture(request, course_slug, lecturepk, lecture_slug):
    lecture_list = get_object_or_404(Lecture, pk=lecturepk)
    paginator = Paginator(lecture_list, 1)
    page_request_var = 'page'
    page = request.GET.get(page_request_var)
    try:
        lecture = paginator.page(page)
    except PageNotAnInteger:
        lecture = paginator.page(1)
    except EmptyPage:
        lecture = paginator.page(paginator.num_pages)
    context = {
        "object_list": lecture,
        "title": "List",
        "page_request_var": page_request_var
    }
    return render(request, 'courses/view_lecture.html', context)


def course_landing_page(request, course_slug):
    course = Course.objects.get(slug=course_slug)
    return render(request, 'courses/course_landing_page.html', {'course': course})


def all_courses(request):
    courses = Course.objects.order_by('-release_date')
    return render(request, 'courses/all_courses.html', {'courses': courses})

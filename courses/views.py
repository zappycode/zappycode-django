from django.shortcuts import render, get_object_or_404

from .models import Lecture, Course


# First approach is just changing lecture.preview rom False to True.
# So it's view which just render standard lecture view only changing one value.

# def view_lecture4all(request, course_slug, lecturepk, lecture_slug, access):
#
#     lecture = get_object_or_404(Lecture, pk=lecturepk)
#     lecture.preview = True
#     return render(request, 'courses/view_lecture.html', {'lecture': lecture})

# its works but we talk about html overriding, specialy if statement. second approach show it.
# There no reason to chang hole view_lecture.html. just override else statement.
def view_lecture4all_second(request, course_slug, lecturepk, lecture_slug, access):
    lecture = get_object_or_404(Lecture, pk=lecturepk)
    return render(request, 'courses/view_lecture_4all.html', {'lecture': lecture})

def view_lecture(request, course_slug, lecturepk, lecture_slug):
    lecture = get_object_or_404(Lecture, pk=lecturepk)
    return render(request, 'courses/view_lecture.html', {'lecture': lecture})

def course_landing_page(request, course_slug):
    course = Course.objects.get(slug=course_slug)
    return render(request, 'courses/course_landing_page.html', {'course': course})


def all_courses(request):
    courses = Course.objects.order_by('-release_date')
    return render(request, 'courses/all_courses.html', {'courses': courses})

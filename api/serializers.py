from rest_framework.fields import CharField

from courses.models import Course, Section, Lecture
from rest_framework import serializers


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'release_date', 'image', 'title', 'subtitle', 'promo_download_url']


class LectureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecture
        fields = ['id', 'title', 'section', 'number', 'text', 'thumbnail_url', 'download_url', 'lecture_url']


class SectionSerializer(serializers.ModelSerializer):
    lectures = LectureSerializer(read_only=True, many=True)

    class Meta:
        model = Section
        fields = ['id', 'title', 'course', 'number', 'lectures']


class CourseWithSectionsAndLecturesSerializer(serializers.ModelSerializer):
    sections = SectionSerializer(read_only=True, many=True)

    class Meta:
        model = Course
        fields = ['id', 'release_date', 'image', 'title', 'subtitle', 'promo_download_url', 'sections']

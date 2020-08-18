from operator import itemgetter

from django.db import models
from django.core.validators import MinValueValidator
from django.utils.text import slugify
import requests
import environ
from tkinter import filedialog
from tkinter import *
env = environ.Env()
environ.Env.read_env()


class Course(models.Model):
    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='course_images')
    vimeo_promo_video_id = models.CharField(max_length=50)
    release_date = models.DateField()
    first_lecture = models.ForeignKey(to='Lecture', on_delete=models.DO_NOTHING)
    download_link = models.URLField(blank=True)
    published = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def sorted_sections(self):
        return self.section_set.order_by('number')


class Section(models.Model):
    title = models.CharField(max_length=255)
    course = models.ForeignKey(to=Course, on_delete=models.CASCADE)
    number = models.IntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return self.title

    def sorted_lectures(self):
        return self.lecture_set.order_by('number')


class Lecture(models.Model):
    title = models.CharField(max_length=255)
    vimeo_video_id = models.CharField(max_length=50, blank=True)
    section = models.ForeignKey(to=Section, on_delete=models.CASCADE)
    number = models.IntegerField(validators=[MinValueValidator(1)])
    text = models.TextField(blank=True)
    preview = models.BooleanField(default=False)
    thumbnail_url = models.URLField(blank=True, null=True)
    download_url = models.URLField(blank=True, null=True)

    def slug(self):
        return slugify(self.title)

    def __str__(self):
        return self.title

    def next_lecture(self):
        # retrieving all the course lectures,
        # exclude all from sections lower than section of actual element
        # and order set by sections and numbers
        __lectures = self.__class__.objects.filter(
            section__course_id=self.section.course.id
        ).order_by('section_id', 'number').exclude(section_id__lt=self.section_id)

        # last() lecture of the course are specific one
        # - has got no any next element
        if self.id == __lectures.last().id:
            return False
        else:
            # threw out from the set all lectures
            # - earlier and actual - after return first element
            __next_lectures = __lectures.exclude(section_id=self.section_id, number__lte=self.number)
            return __next_lectures.first()

    def prev_lecture(self):
        # retrieving all the course lectures,
        # exclude all from sections greater than section of actual element
        # and order set by sections and numbers
        __lectures = self.__class__.objects.filter(
            section__course_id=self.section.course.id
        ).order_by('section_id', 'number').exclude(section_id__gt=self.section_id)

        # first() lecture of the course is specific one - has got no any prev element
        if self.id == __lectures.first().id:
            return False
        else:
            # # threw out from the __lecture set all lectures
            # - later and actual one - after it return last element
            __prev_lectures = __lectures.exclude(section_id=self.section_id, number__gte=self.number)
            return __prev_lectures.last()

    def get_thumbnail_url(self):
        print(env.str('VIMEO_BEARER', default=''))
        headers = {'Authorization': 'bearer ' + env.str('VIMEO_BEARER', default='')}
        video_data = requests.get('https://api.vimeo.com/videos/' + str(self.vimeo_video_id) + '/?sizes=1920', headers=headers)
        try:
            thumb_url = video_data.json()['pictures']['sizes'][0]['link']
            return thumb_url
        except KeyError:
            return None

    def get_download_url(self):
        headers = {'Authorization': 'bearer ' + env.str('VIMEO_BEARER', default='')}
        video_data = requests.get('https://api.vimeo.com/videos/'
                                  + str(self.vimeo_video_id) + '/?fields=files', headers=headers)
        try:
            download_url = video_data.json()['files'][1]['link']
            return download_url
        except KeyError:
            return None

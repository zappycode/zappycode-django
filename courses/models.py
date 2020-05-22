from django.db import models
from django.core.validators import MinValueValidator
from django.utils.text import slugify


class Course(models.Model):
    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='course_images')
    vimeo_promo_video_id = models.CharField(max_length=50)
    release_date = models.DateField()
    first_lecture = models.ForeignKey(to='Lecture', on_delete=models.DO_NOTHING)

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

    def slug(self):
        return slugify(self.title)

    def __str__(self):
        return self.title

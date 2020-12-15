import readtime

from sitewide.models import ZappyUser
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from imagekit.models import ProcessedImageField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from django.utils import timezone
from tinymce.models import HTMLField

STATUS_CHOICES = (
    ('P', 'Published'),
    ('D', 'Draft'),
)


class PostsManager(models.Manager):
    def get_queryset(self):
        '''Returns all posts in queryset'''
        return super().get_queryset()

    def published(self):
        '''Returns a queryset of all published posts'''
        return self.get_queryset().filter(status='P')


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = HTMLField(null=True)
    member_content = HTMLField(null=True, blank=True)

    author = models.ForeignKey(ZappyUser, on_delete=models.CASCADE, null=True, blank=True)
    preview_image = ProcessedImageField(
        blank=True,
        upload_to='images/tutorials/',
    )
    thumbnail = ImageSpecField(
        source='preview_image',
        processors=[ResizeToFill(250, 200)],
        format='JPEG',
        options={'quality': 100}
    )
    published = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=1,
                              choices=STATUS_CHOICES,
                              default='D')

    objects = PostsManager()

    class Meta:
        ordering = ('-published',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('posts:view_post', kwargs={'post_pk': self.id, 'post_slug': slugify(self.title)})

    def get_read_time(self):
        ''' Returns the read time of the Content body '''
        string = str(self.content)
        result = readtime.of_html(string)
        return result

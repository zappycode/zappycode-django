import readtime

from django.db import models
from sitewide.models import ZappyUser
from django.urls import reverse
from django_extensions.db.fields import AutoSlugField
from django.utils import timezone
from django_quill.fields import QuillField
from imagekit.models import ProcessedImageField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from taggit.managers import TaggableManager
from django.db.models import Count

STATUS_CHOICES = (
    ('P', 'Published'),
    ('D', 'Draft'),
)   

class TutorialManager(models.Manager):
    def get_queryset(self):
        '''Returns all tutorials in queryset'''
        return super().get_queryset()

    def published(self):
        '''Returns a queryset of all published tutorials'''
        return self.get_queryset().filter(status='P')

    def get_similar_tutorials(self, obj):
        '''Returns a queryset of 3 tutorials similar to the current object'''
        tutorial = self.published().get(slug=obj.slug)
        tutorial_tags_ids = tutorial.tags.values_list('id', flat=True)
        similar_tutorials = self.published().filter(tags__in=tutorial_tags_ids).exclude(id=tutorial.id)
        similar_tutorials = similar_tutorials.annotate(same_tags=Count('tags')).order_by('-same_tags', '-published')[:3]
        return similar_tutorials

class Tutorial(models.Model):
    title = models.CharField(max_length=200)
    slug = AutoSlugField(
        populate_from='title',
        editable=True
    )
    author = models.ForeignKey(ZappyUser, on_delete=models.CASCADE, related_name="tutorials")
    preview_image = ProcessedImageField(
        blank=True,
        upload_to='images/tutorials/',
        processors=[ResizeToFill(900,650)],
        format='JPEG',
        options={'quality':85}
    )
    thumbnail = ImageSpecField(
        source='preview_image',
        processors=[ResizeToFill(250,200)],
        format='JPEG',
        options={'quality':100}
    )
    content = QuillField()
    published = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=3,
                              choices=STATUS_CHOICES,
                              default='D')
    tags = TaggableManager()

    objects = TutorialManager()

    class Meta:
        ordering = ('-published',)

    def __str__(self):
        '''Returns Object Title and Author'''
        return f"{self.title} by {self.author}"

    def get_absolute_url(self):
        '''Returns the tutorial URL for a specific object'''
        return reverse('tutorials:tutorials_detail', kwargs={
            'slug': self.slug,
        })
    
    def get_read_time(self):
        ''' Returns the read time of the HTML body '''
        string = str(self.content)
        result = readtime.of_html(string)
        return result


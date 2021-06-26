from django.db import models
from taggit.managers import TaggableManager

class Challenge(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    starting_code = models.TextField(null=True,blank=True)
    answer_code = models.TextField()
    tags = TaggableManager()

    def __str__(self):
        return self.title
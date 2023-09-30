from django.db import models
import uuid
from django.urls import reverse

class SendIt(models.Model):
	uuid = models.UUIDField(default=uuid.uuid4)
	name = models.CharField(max_length=255)
	url = models.URLField()
	
	def __str__(self):
		return f'{self.name} - {self.url}'
		
	def get_absolute_url(self):
		return reverse('send:sendit', kwargs={'redirect_uuid': self.uuid})
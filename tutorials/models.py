from .blocks import VideoBlock
from django.db import models
from wagtail.core import blocks
from wagtail.core.models import Page
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, StreamFieldPanel
from wagtail.search import index
from wagtail.images.blocks import ImageChooserBlock
from wagtailcodeblock.blocks import CodeBlock
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase
import readtime

class TutorialPageTag(TaggedItemBase):
	content_object = ParentalKey(
		'TutorialPage',
		related_name='tagged_items',
		on_delete=models.CASCADE
	)

class TutorialPage(Page):
	date = models.DateField("Post date")
	intro = models.CharField(max_length=250)
	body = StreamField([
		('paragraph', blocks.RichTextBlock()),
		('image', ImageChooserBlock()),
		('code', CodeBlock(label='Code', default_language='python')),
		('video', VideoBlock()),
	])
	tags = ClusterTaggableManager(through=TutorialPageTag, blank=True)

	search_fields = Page.search_fields + [
		index.SearchField('intro'),
		index.SearchField('body'),
	]

	content_panels = Page.content_panels + [
		MultiFieldPanel([
			FieldPanel('date'),
			FieldPanel('intro'),
			FieldPanel('tags'),
		], heading="Tutorial Info"),
		StreamFieldPanel('body'),
	]
	
	def get_read_time(self):
		''' Returns the read time of the Content body '''
		string = str(self.body)
		result = readtime.of_html(string)
		return result

from .blocks import VideoBlock
from django.db import models
from wagtail.core import blocks
from wagtail.core.models import Page
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, StreamFieldPanel
from wagtail.search import index
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtailcodeblock.blocks import CodeBlock
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase
from courses.models import Course
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
	promo_image = models.ForeignKey(
		'wagtailimages.Image',
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name='+'
	)
	body = StreamField([
		('paragraph', blocks.RichTextBlock(features=['h2', 'h3', 'h4', 'h5', 'bold', 'italic', 'ol', 'ul', 'hr', 'link', 'document-link', 'code', 'superscript', 'subscript', 'strikethrough', 'blockquote'])),
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
			ImageChooserPanel('promo_image'),
			FieldPanel('tags'),
			FieldPanel('owner')
		], heading="Tutorial Info"),
		StreamFieldPanel('body'),
	]
	
	def get_context(self, request):
		context = super().get_context(request)

		courses = Course.objects.filter(tags__name__in=self.tags.all()).distinct()
		context['courses'] = courses
		
		return context
	
	def get_read_time(self):
		''' Returns the read time of the Content body '''
		string = str(self.body)
		result = readtime.of_html(string)
		return result
		
class HomePage(Page):
	 
	 def get_context(self, request):
		 context = super().get_context(request)
		 tutorials = TutorialPage.objects.live().order_by('-first_published_at')
		 context['tutorials'] = tutorials
		 return context

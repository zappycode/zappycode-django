from wagtail.core.blocks import StructBlock, CharBlock

class VideoBlock(StructBlock):
	video = CharBlock(label="YouTube ID")

	class Meta:
		template = "tutorials/video_card_block.html"
		icon = "media"
		label = "YouTube Video"
		
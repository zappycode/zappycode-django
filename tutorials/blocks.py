from wagtail.core.blocks import StructBlock, CharBlock

class VideoBlock(StructBlock):
	video = CharBlock()

	class Meta:
		template = "tutorials/video_card_block.html"
		icon = "media"
		label = "YouTube ID"
		
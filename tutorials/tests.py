from django.test import TestCase
from django.urls import reverse

class TestPage(TestCase):
    def test_tutorials_listing_page(self):
        response = self.client.get(reverse("tutorials:tutorials_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutorials/tutorials_list.html')
    
    def test_tutorials_detail_page(self):
        response = self.client.get(reverse("tutorials:tutorials_detail"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutorials/tutorials_detail.html')
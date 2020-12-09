from django.contrib import sitemaps
from django.urls import reverse
from money.models import Month
from courses.models import Course

class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return ['home', 'all_courses', 'money:home', 'pricing', 'account_login', 'account_signup']

    def location(self, item):
        return reverse(item)

class MoneySitemap(sitemaps.Sitemap):
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return Month.objects.all()

class CourseSitemap(sitemaps.Sitemap):
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        return Course.objects.all()
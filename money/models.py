from django.db import models
import calendar
from django.utils.text import slugify


class Month(models.Model):
    month = models.IntegerField()
    year = models.IntegerField()
    expenses = models.DecimalField(max_digits=10, decimal_places=2)
    revenue = models.DecimalField(max_digits=10, decimal_places=2)
    body = models.TextField()
    youtube_id = models.CharField(max_length=255)

    def __str__(self):
        return self.title()

    def title(self):
        return f'{self.month_string()} {self.year} Money Report'

    def slug(self):
        return slugify(self.title())

    def month_string(self):
        return calendar.month_name[self.month]

    def profit_or_loss(self):
        return self.revenue - self.expenses

    def profit_or_loss_abs(self):
        return abs(self.revenue - self.expenses)

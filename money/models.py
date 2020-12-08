from django.db import models
import calendar
import json
from django.utils.text import slugify

class MonthManager(models.Manager):
    def to_json(self):
        """ Returns all objects as a list of JSON objects in chronological order with format {"month": month, "mrr": mrr} """
        qs = self.get_queryset().order_by('year', 'month').values("month", "mrr")
        list_of_dicts = list(qs)
        for single_dict in list_of_dicts:
            single_dict["mrr"] = str(single_dict["mrr"])
            single_dict["month"] = calendar.month_name[single_dict["month"]]
        return json.dumps(list_of_dicts)
        

class Month(models.Model):
    month = models.IntegerField()
    year = models.IntegerField()
    expenses = models.DecimalField(max_digits=10, decimal_places=2)
    revenue = models.DecimalField(max_digits=10, decimal_places=2)
    body = models.TextField()
    youtube_id = models.CharField(max_length=255, null=True, blank=True)
    mrr = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    objects = MonthManager()

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

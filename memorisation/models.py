from datetime import date, timedelta

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import fields

from words.models import Card
from .algorithm import interval


class Practice(models.Model):
    card = models.OneToOneField(
        Card, on_delete=models.CASCADE, related_name="practice")
    next_practice = models.DateField(auto_now_add=True)
    times_practiced = models.PositiveIntegerField(default=1)
    easy_factor = models.FloatField(default=2.5)

    class Meta:
        ordering = ['next_practice']

    def __str__(self):
        return 'practice: "{}"'.format(self.card)

    def set_next_practice(self, rating):
        days, ef = interval(self.times_practiced, rating, self.easy_factor)
        self.next_practice = date.today() + timedelta(days=days)
        self.times_practiced += 1
        self.easy_factor = ef

    def delay(self):
        self.next_practice = date.today() + timedelta(days=1)

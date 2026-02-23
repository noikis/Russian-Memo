from django.db import models
from datetime import date, timedelta

from words.models import Card
from .algorithm import interval


class CardPractice(models.Model):
    card = models.OneToOneField(Card, on_delete=models.CASCADE, related_name="practice")
    state = models.CharField(max_length=255)
    due = models.DateField()
    interval = models.IntegerField()
    ease_factor = models.IntegerField()
    reps = models.IntegerField()
    lapses = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "card_practice"
        ordering = ["due"]

    def __str__(self):
        return 'practice: "{}"'.format(self.card)

    # Backward-compatible helpers for existing call sites.
    def set_next_practice(self, rating):
        days, ef = interval(self.reps, rating, self.ease_factor)
        self.due = date.today() + timedelta(days=days)
        self.reps += 1
        self.ease_factor = int(ef)

    def delay(self):
        self.due = date.today() + timedelta(days=1)


class CardReview(models.Model):
    practice = models.ForeignKey(CardPractice, on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField()
    reviewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "card_reviews"


class Practice(CardPractice):
    class Meta:
        proxy = True

from datetime import date

from django.apps import apps
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from account.models import User


class Deck(models.Model):
    title = models.CharField(max_length=100, unique=True, null=True, blank=True)
    color = models.CharField(max_length=255)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="decks")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        db_table = "decks"

    def __str__(self):
        return self.title


class Card(models.Model):
    word = models.CharField(max_length=255)
    explanation = models.TextField(null=True, blank=True)
    translation = models.TextField(null=True, blank=True)
    synonymes = models.TextField(null=True, blank=True)
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name="cards")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        db_table = "cards"

    def __str__(self):
        return self.word


@receiver(post_save, sender=Card)
def create_initial_practice(sender, instance, created, **kwargs):
    if not created:
        return

    Practice = apps.get_model("memorisation", "Practice")
    Practice.objects.get_or_create(
        card=instance,
        defaults={
            "state": "new",
            "due": date.today(),
            "interval": 0,
            "ease_factor": 2,
            "reps": 0,
            "lapses": 0,
        },
    )

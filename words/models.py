from django.db import models
from account.models import Student


class Deck(models.Model):
    category = models.CharField(
        max_length=100,
        default="New Deck",
        verbose_name="Название",
    )
    color = models.CharField(
        default="#00bcd4",
        max_length=30,
        verbose_name="Цвет",
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='decks',
        verbose_name="Студент",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата удаления",
    )

    class Meta:
        verbose_name = "Колода"
        verbose_name_plural = "Колоды"

    def __str__(self):
        return self.category


class Card(models.Model):
    deck = models.ForeignKey(
        Deck, on_delete=models.CASCADE, related_name='cards')
    word = models.CharField(max_length=100, blank=False, null=False)
    image = models.ImageField(upload_to='cards/', blank=True)
    explanation = models.TextField(max_length=500, blank=True)
    translation = models.CharField(max_length=55, blank=True)
    synonymes = models.TextField(max_length=255, blank=True)

    def __str__(self):
        return self.word

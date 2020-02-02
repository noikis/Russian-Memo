from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)


class Student(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True)
    score = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.user.username

    def get_all_cards(self, Card):
        queryset = Card.objects.filter(deck__student__user=self.user)
        return queryset

    def get_all_decks(self, Deck):
        queryset = Deck.objects.filter(student__user=self.user)
        return queryset

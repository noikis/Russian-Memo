from django.db import models

# Create your models here.


class Card(models.Model):
    word = models.CharField(max_length=55, blank=False, null=False)
    image = models.ImageField(upload_to='cards/', blank=True)
    explanation = models.TextField(max_length=500, blank=True)
    translation = models.CharField(max_length=55, blank=True)
    synonymes = models.TextField(max_length=255, blank=True)

    def __str__(self):
        return self.word

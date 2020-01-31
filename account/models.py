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


class Level(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

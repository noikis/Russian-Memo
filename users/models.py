from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):

    def create_superuser(self, username, email, password=None):
        user = self.model(username=username)
        user.set_password(password)
        user.email = self.model(email=email)
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.is_teacher = True
        user.is_student = False

        user.save(using=self._db)
        return user


class User(AbstractUser):
    is_student = models.BooleanField()
    is_teacher = models.BooleanField()

    objects = UserManager()

    def __str__(self):
        return self.username


class Student(User):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, parent_link=True)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'


class Teacher(User):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, parent_link=True)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Преподователь'
        verbose_name_plural = 'Преподователи'

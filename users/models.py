from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):

    def create_user(self, username, email, first_name, last_name, is_student, is_teacher,  password=None):
        if not email:
            raise ValueError('Электронная почта объязательнная.')

        user = self.model(
            username=username,
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
        )

        user.set_password(password)
        user.is_student = is_student
        user.is_teacher = is_teacher

        user.is_admin = False
        user.is_superuser = False
        user.is_staff = False
        user.save(using=self._db)
        # "using=self._db" -> save it in this database
        return user

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

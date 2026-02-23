from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)
    password = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    deleted_at = models.DateTimeField(null=True, blank=True)
    roles = models.ManyToManyField("Role", through="UserRole", related_name="users")

    class Meta:
        db_table = "users"


class Role(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = "roles"

    def __str__(self):
        return self.name


class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_roles")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="user_roles")

    class Meta:
        db_table = "user_roles"
        unique_together = ("user", "role")


class ExternalIdentity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="external_identities")
    provider = models.CharField(max_length=255)
    provider_user_id = models.BigIntegerField()
    username = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=150, null=True, blank=True)
    last_name = models.CharField(max_length=150, null=True, blank=True)
    photo_url = models.TextField(null=True, blank=True)
    auth_date = models.BigIntegerField(null=True, blank=True)
    last_login_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "external_identities"
        unique_together = ("provider", "provider_user_id")

    def __str__(self):
        return "{}:{}".format(self.provider, self.provider_user_id)


class Student(User):
    class Meta:
        proxy = True

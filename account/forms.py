from django.contrib.auth.forms import UserCreationForm
from django.db import transaction

from .models import Role, User


class TeacherSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            role, _ = Role.objects.get_or_create(name="teacher")
            user.roles.add(role)
        return user


class StudentSignUpForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            role, _ = Role.objects.get_or_create(name="student")
            user.roles.add(role)
        return user

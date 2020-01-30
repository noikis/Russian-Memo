from django.contrib import admin
from django.contrib.auth.models import Group
from material.admin.sites import site

from .models import User, Student


admin.site.register(User)
admin.site.register(Student)


# site.unregister(Group)

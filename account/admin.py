from django.contrib import admin
from django.contrib.auth.models import Group
from material.admin.sites import site

from .models import User


admin.site.register(User)


# site.unregister(Group)

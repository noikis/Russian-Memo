from django.contrib import admin
from django.contrib.auth.models import Group


from .models import Student, Teacher
admin.site.register(Student)
admin.site.register(Teacher)

from django.contrib import admin

from .models import Question, Quiz, Answer
# Register your models here.
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Answer)

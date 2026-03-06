from django.contrib import admin

from .models import Question, Quiz, Answer, QuizAttempt, SelectedAnswer
# Register your models here.
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(QuizAttempt)
admin.site.register(SelectedAnswer)

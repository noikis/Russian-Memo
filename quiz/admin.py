from django.contrib import admin

from .models import Question, Quiz, Answer, TakenQuiz, StudentAnswer
# Register your models here.
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(TakenQuiz)

from django.urls import path, include

from .views import QuizCreateView

app_name = 'quiz'

urlpatterns = [
    path('add/', QuizCreateView.as_view(), name='add_quiz'),
]

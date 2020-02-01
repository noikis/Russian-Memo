from django.urls import path, include

from .views import QuizCreateView, QuizListView

app_name = 'quiz'

urlpatterns = [
    path('add/', QuizCreateView.as_view(), name='add_quiz'),
    path('list/', QuizListView.as_view(), name='quiz_list'),
]

from django.urls import path, include

from .views import (QuizCreateView, QuizListView,
                    QuizUpdateView, QuizDeleteView, question_add)

app_name = 'quiz'

urlpatterns = [
    path('add/', QuizCreateView.as_view(), name='add_quiz'),
    path('list/', QuizListView.as_view(), name='quiz_list'),
    path('<int:pk>/', QuizUpdateView.as_view(), name='quiz_update'),
    path('<int:pk>/delete/', QuizDeleteView.as_view(), name='quiz_delete'),
    path('<int:pk>/question/add/', question_add, name='question_add'),
]

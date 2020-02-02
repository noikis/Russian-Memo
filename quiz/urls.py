from django.urls import path, include

from .views.teachers import (QuizCreateView, QuizListView, QuizUpdateView,
                             QuizDeleteView, QuestionDeleteView, question_add, question_update)

app_name = 'quiz'

urlpatterns = [
    path('', QuizListView.as_view(), name='quiz_list'),
    path('add/', QuizCreateView.as_view(), name='add_quiz'),
    path('<int:pk>/', QuizUpdateView.as_view(), name='quiz_update'),
    path('<int:pk>/delete/', QuizDeleteView.as_view(), name='quiz_delete'),
    path('<int:pk>/question/add/', question_add, name='question_add'),
    path('<int:quiz_pk>/question/<int:question_pk>/',
         question_update, name='question_update'),
    path('<int:quiz_pk>/question/<int:question_pk>/delete',
         QuestionDeleteView.as_view(), name='question_delete'),
]

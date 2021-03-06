from django.urls import path, include

from .views.teachers import QuizResultsView as TeacherQuizResultsView
from .views.teachers import (QuizCreateView, QuizListView, QuizUpdateView,
                             QuizDeleteView, QuestionDeleteView, question_add, question_update)

from .views.students import QuizListView as StudentQuizListView
from .views.students import take_quiz, TakenQuizListView, QuizResultsView
app_name = 'quiz'

urlpatterns = [
    # teacher urls
    path('', QuizListView.as_view(), name='quiz_list'),
    path('add/', QuizCreateView.as_view(), name='add_quiz'),
    path('<int:pk>/', QuizUpdateView.as_view(), name='quiz_update'),
    path('<int:pk>/delete/', QuizDeleteView.as_view(), name='quiz_delete'),
    path('<int:pk>/results/', TeacherQuizResultsView.as_view(),
         name='question_results_teacher'),
    path('<int:pk>/question/add/', question_add, name='question_add'),
    path('<int:quiz_pk>/question/<int:question_pk>/',
         question_update, name='question_update'),
    path('<int:quiz_pk>/question/<int:question_pk>/delete',
         QuestionDeleteView.as_view(), name='question_delete'),

    # student urls
    path('list/', StudentQuizListView.as_view(), name='quiz_list_student'),
    path('take_quiz/<int:pk>/', take_quiz, name='take_quiz'),
    path('taken/', TakenQuizListView.as_view(), name='taken_quiz'),
    path('<int:pk>/studentresults/', QuizResultsView.as_view(),
         name='student_quiz_results'),

]

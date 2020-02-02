from django import forms
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.db.models import Count


from ..models import Quiz, Question, Answer
from account.decorators import student_required


@method_decorator([login_required, student_required], name='dispatch')
class QuizListView(ListView):
    model = Quiz
    ordering = ('name', )
    context_object_name = 'quizzes'
    template_name = 'quiz/students/quiz_list.html'

    def get_queryset(self):
        student = self.request.user.student
        taken_quizzes = student.quizzes.values_list('pk', flat=True)
        queryset = Quiz.objects.exclude(pk__in=taken_quizzes) \
            .annotate(questions_count=Count('questions')) \
            .filter(questions_count__gt=0)
        return queryset

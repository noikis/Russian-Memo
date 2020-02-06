from django import forms
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView, View
from django.db import transaction
from django.db.models import Count, Sum


from ..models import Quiz, Question, Answer, TakenQuiz
from ..forms import TakeQuizForm
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


@method_decorator([login_required, student_required], name='dispatch')
class TakenQuizListView(ListView):
    model = TakenQuiz
    context_object_name = 'taken_quizzes'
    template_name = 'quiz/students/taken_quiz.html'

    def get_queryset(self):
        queryset = self.request.user.student.taken_quizzes \
            .order_by('date')
        return queryset


@method_decorator([login_required, student_required], name='dispatch')
class QuizResultsView(View):
    template_name = 'quiz/students/quiz_result.html'

    def get(self, request, *args, **kwargs):
        quiz = Quiz.objects.get(id=kwargs['pk'])
        taken_quiz = TakenQuiz.objects.filter(
            student=request.user.student, quiz=quiz)

        if not taken_quiz:
            """
            Don't show the result if the user didn't attempted the quiz
            """
            return redirect('quiz:dashboard')
        questions = Question.objects.filter(quiz=quiz)

        # questions = self.form_class(initial=self.initial)
        context = {
            'questions': questions,
            'quiz': quiz,
            'percentage': taken_quiz[0].percentage
        }
        return render(request, self.template_name, context)


@login_required
@student_required
def take_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    student = request.user.student

    if student.quizzes.filter(pk=pk).exists():
        return render(request, 'students/taken_quiz.html')

    total_questions = quiz.questions.count()
    unanswered_questions = student.get_unanswered_questions(quiz)
    total_unanswered_questions = unanswered_questions.count()
    progress = 100 - \
        round(((total_unanswered_questions - 1) / total_questions) * 100)
    question = unanswered_questions.first()

    if request.method == 'POST':
        form = TakeQuizForm(question=question, data=request.POST)
        if form.is_valid():
            with transaction.atomic():
                student_answer = form.save(commit=False)
                student_answer.student = student
                student_answer.save()
                if student.get_unanswered_questions(quiz).exists():
                    return redirect('quiz:take_quiz', pk)
                else:
                    correct_answers = student.quiz_answers.filter(
                        answer__question__quiz=quiz, answer__is_correct=True).count()
                    percentage = round(
                        (correct_answers / total_questions) * 100.0, 2)
                    TakenQuiz.objects.create(
                        student=student, quiz=quiz, score=correct_answers, percentage=percentage)
                    student.score = TakenQuiz.objects.filter(
                        student=student).aggregate(Sum('score'))['score__sum']
                    student.save()
                    if percentage < 50.0:
                        messages.warning(request, 'Better luck next time! Your score for the quiz %s was %s.' % (
                            quiz.name, percentage))
                    else:
                        messages.success(request, 'Congratulations! You completed the quiz %s with success! You scored %s points.' % (
                            quiz.name, percentage))
                    return redirect('quiz:quiz_list_student')
    else:
        form = TakeQuizForm(question=question)

    return render(request, 'quiz/students/take_quiz_form.html', {
        'quiz': quiz,
        'question': question,
        'form': form,
        'progress': progress,
        'answered_questions': total_questions - total_unanswered_questions,
        'total_questions': total_questions
    })

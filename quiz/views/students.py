from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, View
from django.db import transaction
from django.db.models import Count
from django.utils import timezone


from ..models import Quiz, Question, QuizAttempt, SelectedAnswer
from ..forms import TakeQuizForm
from account.decorators import student_required


@method_decorator([login_required, student_required], name='dispatch')
class QuizListView(ListView):
    model = Quiz
    ordering = ('name', )
    context_object_name = 'quizzes'
    template_name = 'quiz/students/quiz_list.html'

    def get_queryset(self):
        student = self.request.user
        taken_quizzes = QuizAttempt.objects.filter(
            student=student, finished_at__isnull=False
        ).values_list('quiz_id', flat=True)
        queryset = Quiz.objects.exclude(pk__in=taken_quizzes) \
            .annotate(questions_count=Count('questions')) \
            .filter(questions_count__gt=0)
        return queryset


@method_decorator([login_required, student_required], name='dispatch')
class QuizAttemptListView(ListView):
    model = QuizAttempt
    context_object_name = 'taken_quizzes'
    template_name = 'quiz/students/taken_quiz.html'

    def get_queryset(self):
        return QuizAttempt.objects.filter(
            student=self.request.user,
            finished_at__isnull=False,
        ).order_by('-finished_at', '-started_at')


@method_decorator([login_required, student_required], name='dispatch')
class QuizResultsView(View):
    template_name = 'quiz/students/quiz_result.html'

    def get(self, request, *args, **kwargs):
        quiz = Quiz.objects.get(id=kwargs['pk'])
        attempt = QuizAttempt.objects.filter(
            student=request.user, quiz=quiz, finished_at__isnull=False
        ).order_by('-finished_at', '-started_at').first()

        if not attempt:
            """
            Don't show the result if the user didn't attempted the quiz
            """
            return redirect('quiz:dashboard')
        questions = Question.objects.filter(quiz=quiz)

        # questions = self.form_class(initial=self.initial)
        context = {
            'questions': questions,
            'quiz': quiz,
            'percentage': attempt.percentage
        }
        return render(request, self.template_name, context)


@login_required
@student_required
def take_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    student = request.user

    if QuizAttempt.objects.filter(student=student, quiz=quiz, finished_at__isnull=False).exists():
        return redirect('quiz:taken_quiz')

    total_questions = quiz.questions.count()
    if total_questions == 0:
        messages.warning(request, 'В этом тесте нет вопросов.')
        return redirect('quiz:quiz_list_student')

    attempt = (
        QuizAttempt.objects.filter(student=student, quiz=quiz, finished_at__isnull=True)
        .order_by('-started_at')
        .first()
    )
    if attempt is None:
        attempt = QuizAttempt.objects.create(
            student=student,
            quiz=quiz,
            score=0,
            percentage=0,
        )

    answered_question_ids = attempt.selected_answers.filter(
        selected_answer__isnull=False
    ).values_list('selected_answer__question_id', flat=True)
    unanswered_questions = quiz.questions.exclude(
        id__in=answered_question_ids
    ).order_by('position', 'id')
    total_unanswered_questions = unanswered_questions.count()
    if total_unanswered_questions == 0:
        correct_answers = attempt.selected_answers.filter(
            selected_answer__is_correct=True
        ).count()
        percentage = round((correct_answers / total_questions) * 100.0, 2)
        attempt.score = correct_answers
        attempt.percentage = percentage
        attempt.finished_at = timezone.now()
        attempt.save()
        if percentage < 50.0:
            messages.warning(
                request,
                'В следующий раз получится лучше! Ваш результат в тесте "%s" — %s.' % (
                    quiz.name, percentage)
            )
        else:
            messages.success(
                request,
                'Поздравляем! Вы успешно прошли тест "%s". Ваш результат — %s.' % (
                    quiz.name, percentage)
            )
        return redirect('quiz:quiz_list_student')

    progress = 100 - \
        round(((total_unanswered_questions - 1) / total_questions) * 100)
    question = unanswered_questions.first()

    if request.method == 'POST':
        form = TakeQuizForm(question=question, data=request.POST)
        if form.is_valid():
            with transaction.atomic():
                selected_answer = form.cleaned_data['answer']
                already_answered = attempt.selected_answers.filter(
                    selected_answer__question=question
                ).exists()
                if not already_answered:
                    SelectedAnswer.objects.create(
                        attempt=attempt,
                        selected_answer=selected_answer,
                    )

                remaining = quiz.questions.exclude(
                    id__in=attempt.selected_answers.filter(
                        selected_answer__isnull=False
                    ).values_list('selected_answer__question_id', flat=True)
                )
                if remaining.exists():
                    return redirect('quiz:take_quiz', pk)
                else:
                    correct_answers = attempt.selected_answers.filter(
                        selected_answer__is_correct=True
                    ).count()
                    percentage = round(
                        (correct_answers / total_questions) * 100.0, 2)
                    attempt.score = correct_answers
                    attempt.percentage = percentage
                    attempt.finished_at = timezone.now()
                    attempt.save()
                    if percentage < 50.0:
                        messages.warning(request, 'В следующий раз получится лучше! Ваш результат в тесте "%s" — %s.' % (
                            quiz.name, percentage))
                    else:
                        messages.success(request, 'Поздравляем! Вы успешно прошли тест "%s". Ваш результат — %s.' % (
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

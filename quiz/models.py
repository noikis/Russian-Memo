from django.db import models

from account.models import User


class Quiz(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="quizzes")
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "quizzes"
        verbose_name_plural = "Quizzes"

    def __str__(self):
        return self.name


class Question(models.Model):
    text = models.TextField()
    position = models.IntegerField()
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "questions"

    def __str__(self):
        return self.text


class Answer(models.Model):
    text = models.TextField()
    is_correct = models.BooleanField(default=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "answers"

    def __str__(self):
        return self.text


class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="quiz_attempts")
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField()
    percentage = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        db_table = "quiz_attempts"

    def __str__(self):
        return "id_{}".format(self.pk)


class SelectedAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name="selected_answers")
    selected_answer = models.ForeignKey(
        Answer, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "selected_answers"


class TakenQuiz(QuizAttempt):
    class Meta:
        proxy = True


class StudentAnswer(SelectedAnswer):
    class Meta:
        proxy = True

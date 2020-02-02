from django.db import models

from account.models import User, Student


class Quiz(models.Model):
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='quizzes')
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Quizzes"

    def __str__(self):
        return self.name


class Question(models.Model):
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField('Question', max_length=255)

    def __str__(self):
        return self.text


class Answer(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField('Answer', max_length=255)
    is_correct = models.BooleanField('Correct answer', default=False)

    def __str__(self):
        return self.text


class TakenQuiz(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name='taken_quizzes')
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name='taken_quizzes')
    score = models.IntegerField()
    percentage = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Taken Quizzes"


class StudentAnswer(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name='quiz_answers')
    answer = models.ForeignKey(
        Answer, on_delete=models.CASCADE, related_name='+')

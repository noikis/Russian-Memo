from django import template
from quiz.models import StudentAnswer

register = template.Library()


@register.filter(name='field_type')
def field_type(field):
    return field.field.widget.__class__.__name__


@register.simple_tag
def marked_answer(user, opt):
    studentanswer = StudentAnswer.objects.filter(
        student=user.student, answer=opt)
    if studentanswer:
        if opt.is_correct:
            return 'correct'
        return 'wrong'

    return ''

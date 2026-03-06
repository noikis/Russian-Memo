from django import template
from quiz.models import SelectedAnswer


register = template.Library()


@register.filter(name='field_type')
def field_type(field):
    return field.field.widget.__class__.__name__


@register.simple_tag
def marked_answer(user, opt):
    selected = SelectedAnswer.objects.filter(
        attempt__student=user,
        attempt__quiz=opt.question.quiz,
        attempt__finished_at__isnull=False,
        selected_answer=opt,
    )
    if selected:
        if opt.is_correct:
            return 'correct'
        return 'wrong'

    return ''


@register.filter(name='addcss')
def addcss(value, arg):
    css_classes = value.field.widget.attrs.get('class', '').split(' ')
    if css_classes and arg not in css_classes:
        css_classes = ' %s' % (arg)
    return value.as_widget(attrs={'class': css_classes})

from django import template
from memorisation.models import Practice
from datetime import date

register = template.Library()

@register.simple_tag
def to_practice(user):
    student_practice = Practice.objects.filter(
        card__deck__student=user).order_by('next_practice')

    practice_count = student_practice.filter(
        next_practice__lte=date.today()).count()
    
    return practice_count
    


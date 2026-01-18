from django import forms
from django.core.exceptions import ValidationError


def validate_0_5(value):
    if not 0 <= value <= 5:
        raise ValidationError


RATINGS = ((0, 'Забыл'), (1, 'Еле помню'), (2, 'Нужна работа'),
           (3, 'Вспомнил'), (4, 'Знаю'),)


class RatingsForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput)
    rating = forms.ChoiceField(choices=RATINGS)

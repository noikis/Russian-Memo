from django.urls import path

from .views import hangman, speed_typing

app_name = 'memo'


urlpatterns = [
    path('hangman/', hangman, name='hangman'),
    path('translate/', speed_typing, name='speed_typing'),
]

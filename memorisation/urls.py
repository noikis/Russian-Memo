from django.urls import path

from .views import hangman

app_name = 'memo'


urlpatterns = [
    path('hangman/', hangman, name='hangman'),
]

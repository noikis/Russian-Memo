from django.urls import path

from .views import hangman, speed_typing, next_practice_item, process_rating

app_name = 'memo'


urlpatterns = [
    path('hangman/', hangman, name='hangman'),
    path('translate/', speed_typing, name='speed_typing'),
    path('flashcards/', next_practice_item, name='flashcards'),
    path('process_rating/', process_rating, name='process_rating'),
]

from django.urls import path

from .views import DeckCreateView, CardCreateView

app_name = 'words'

urlpatterns = [
    path('deck/add/', DeckCreateView.as_view(), name='deck_add'),
    path('card/add/', CardCreateView.as_view(), name='card_add'),
]

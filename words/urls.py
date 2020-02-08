from django.urls import path

from .views import (DeckCreateView, CardCreateView,
                    DeckListView, CardListView, DeckUpdateView, CardUpdateView)

app_name = 'words'

urlpatterns = [
    path('decks/add/', DeckCreateView.as_view(), name='deck_add'),
    path('decks/', DeckListView.as_view(), name='deck_list'),
    path('<int:pk>/cards/', CardListView.as_view(), name='card_list'),
    path('cards/add/', CardCreateView.as_view(), name='card_add'),
    path('decks/<int:pk>/', DeckUpdateView.as_view(), name='deck_update'),
    path('cards/<int:pk>/', CardUpdateView.as_view(), name='card_update'),
]

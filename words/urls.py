from django.urls import path

from .views import (CardCreateView, DeckListView, CardListView, DeckUpdateView,
                    CardUpdateView, CardDeleteView, DeckDeleteView, deck_create)

app_name = 'words'

urlpatterns = [
    path('decks/add/', deck_create, name='deck_add'),
    path('decks/', DeckListView.as_view(), name='deck_list'),
    path('<int:pk>/cards/', CardListView.as_view(), name='card_list'),
    path('<int:pk>/cards/add/', CardCreateView.as_view(), name='card_add'),
    path('decks/<int:pk>/', DeckUpdateView.as_view(), name='deck_update'),
    path('cards/<int:pk>/', CardUpdateView.as_view(), name='card_update'),
    path('cards/<int:pk>/delete/', CardDeleteView.as_view(), name='card_delete'),
    path('decks/<int:pk>/delete/', DeckDeleteView.as_view(), name='deck_delete'),
]

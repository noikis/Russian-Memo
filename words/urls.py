from django.urls import path

from .views import DeckCreateView, CardCreateView, DeckListView, CardListView

app_name = 'words'

urlpatterns = [
    path('deck/add/', DeckCreateView.as_view(), name='deck_add'),
    path('deck/list/', DeckListView.as_view(), name='deck_list'),
    path('card/list/', CardListView.as_view(), name='card_list'),
    path('card/add/', CardCreateView.as_view(), name='card_add'),
]

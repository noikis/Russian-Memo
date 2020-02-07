from django.urls import path

from .views import DeckCreateView

app_name = 'words'

urlpatterns = [
    path('deck/add/', DeckCreateView.as_view(), name='deck_add'),
]

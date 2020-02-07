from django.shortcuts import render, redirect
from django.core.serializers import serialize
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, ListView, UpdateView


from .models import Card, Deck
from account.decorators import teacher_required, student_required


class DeckCreateView(CreateView):
    model = Deck
    fields = ('category', 'color',)
    template_name = 'words/deck_add.html'

    def form_valid(self, form):
        deck = form.save(commit=False)
        deck.save()
        messages.success(self.request, "Deck created!")
        return redirect('dashboard')


@login_required
def cards(request):
    queryset = Card.objects.filter(deck__student__user=request.user)
    queryset = serialize('json', queryset)
    return HttpResponse(queryset, content_type="application/json")


@login_required
@student_required
def fetch_cards(request):
    return render(request, 'games/fetch_test.html')

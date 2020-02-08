from django.shortcuts import render, redirect
from django.core.serializers import serialize
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView


from .models import Card, Deck
from memorisation.models import Practice
from account.decorators import teacher_required, student_required


@method_decorator([login_required], name='dispatch')
class DeckCreateView(CreateView):
    model = Deck
    fields = ('category', 'color',)
    template_name = 'words/deck_add.html'

    def form_valid(self, form):
        deck = form.save(commit=False)
        deck.save()
        messages.success(self.request, "Deck created!")
        return redirect('account:dashboard')


@method_decorator([login_required], name='dispatch')
class CardCreateView(CreateView):
    model = Card
    fields = '__all__'
    template_name = 'words/card_add.html'

    def form_valid(self, form):
        card = form.save(commit=False)
        card.save()
        practice = Practice(card=card, student=self.request.user.student)
        practice.save()

        messages.success(self.request, "Card created!")
        return redirect('account:dashboard')


@login_required
def cards(request):
    queryset = Card.objects.filter(deck__student__user=request.user)
    queryset = serialize('json', queryset)
    return HttpResponse(queryset, content_type="application/json")


@login_required
@student_required
def fetch_cards(request):
    return render(request, 'games/fetch_test.html')

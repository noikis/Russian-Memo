from django.shortcuts import render
from django.core.serializers import serialize
from django.http import HttpResponse

from .models import Card


def cards(request):
    queryset = Card.objects.all()
    queryset = serialize('json', queryset)
    return HttpResponse(queryset, content_type="application/json")


def fetch_cards(request):
    return render(request, 'games/fetch_test.html')

from django.shortcuts import render
from django.core.serializers import serialize
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from .models import Card
from account.decorators import teacher_required, student_required


@login_required
def cards(request):
    queryset = Card.objects.filter(deck__student__user=request.user)
    queryset = serialize('json', queryset)
    return HttpResponse(queryset, content_type="application/json")


@login_required
@student_required
def fetch_cards(request):
    return render(request, 'games/fetch_test.html')

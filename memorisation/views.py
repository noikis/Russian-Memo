from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, reverse, redirect
from datetime import date

from .forms import RatingsForm
from .models import Practice
from account.decorators import post_required


@login_required
def next_practice_item(request):
    student_practice = Practice.objects.filter(
        card__deck__student=request.user.student).order_by('next_practice')

    practice = student_practice.filter(
        next_practice__lte=date.today())

    if len(practice) > 0:
        practice = practice[0]
        form = RatingsForm(initial={"id": practice.id})
        card = practice.card
        context = {
            'practice': practice,
            'card': card,
            'form': form
        }
        return render(request, 'games/flashcards.html', context)

    else:
        context = {
            'next_practice': student_practice.first().next_practice
        }
        return render(request, 'games/flashcards.html', context)


@post_required
@login_required
def process_rating(request):
    form = RatingsForm(request.POST)
    if form.is_valid():
        practice_item = get_object_or_404(Practice,
                                          pk=int(form.cleaned_data['id']))
        practice_item.set_next_practice(int(form.cleaned_data['rating']))
        practice_item.save()
        return redirect('memo:flashcards')


@post_required
@login_required
def skip_practice(request, practice_id, redirect):
    practice = Practice.objects.get(pk=int(practice_id))
    practice.delay()
    practice.save()
    return HttpResponseRedirect(reverse(redirect))


def hangman(request):
    return render(request, 'games/hangman.html')


def speed_typing(request):
    return render(request, 'games/speed_typing.html')

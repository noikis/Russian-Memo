from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, reverse

from .forms import RatingsForm
from .models import Practice
from account.decorators import post_required


@login_required
def next_practice_item(request, template):
    practice = Practice.objects.filter(
        user=request.user).order_by('next_practice')[0]
    form = RatingsForm(initial={"id": practice.id})
    item = practice.item
    return render(request, template, {
        'practice': practice, 'item': item, 'form': form})


@post_required
@login_required
def process_rating(request, post_save_redirect):
    form = RatingsForm(request.POST)
    if form.is_valid():
        practice_item = get_object_or_404(Practice,
                                          pk=int(form.cleaned_data['id']))
        practice_item.set_next_practice(int(form.cleaned_data['rating']))
        practice_item.save()
        return HttpResponseRedirect(post_save_redirect)


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

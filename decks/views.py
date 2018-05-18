from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.template import loader
# Create your views here.
from .models import Deck


def index(request):
    latest_deck_list = Deck.objects.order_by('-pub_date')[:5]
    context = {
        'latest_deck_list': latest_deck_list,
    }
    return render(request, 'decks/index.html', context)


def detail(request, deck_id):
    # try:
    #     deck = Deck.objects.get(pk=deck_id)
    # except Deck.DoesNotExist:
    #     raise Http404("Deck does not exist.")
    deck = get_object_or_404(Deck, pk=deck_id)

    return render(request, 'decks/detail.html', {'deck': deck})


# def search(request, deck_id_from, deck_id_to):
#     return HttpResponse("You are looking from %s to " % deck_id_from + "%s" % deck_id_to)




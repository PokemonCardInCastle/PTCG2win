from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.http import HttpResponse, Http404, JsonResponse
from django.template import loader
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django_filters.views import FilterView
from django.utils import timezone
from django.views import generic
from decks.japanese_converter import hiragana2katakana, romaji2katakana
from django.views.generic.base import View
from django.db.models import Prefetch
import json
from django.db.models import ObjectDoesNotExist
from pure_pagination.mixins import PaginationMixin
from .models import Deck, DeckCode, Card, CardName, PTCG2winUser, Regulation, ArchType, DeckList, CardBundle
from .filters import DeckFilter
from .forms import DeckRegisterForm
from .proxy_maker import dl_img_and_return_http_response, dl_img_and_return_zip_http_response, CodeInputForm, generate_csv_and_return_response
import urllib.parse
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from random import random

from copy import copy




def index(request):
    latest_deck_list = Deck.objects.order_by('-pub_date')[:5]
    context = {
        'latest_deck_list': latest_deck_list,
        "disable_breadcrumb": True,
    }
    return render(request, 'decks/index.html', context)


def deck_board(request):
    latest_deck_list = Deck.objects.order_by('-pub_date')[:5]
    context = {
        'decks_to_show': latest_deck_list,
        "disable_breadcrumb": False,
    }
    return render(request, 'decks/deck_board.html', context)


def detail(request, deck_id):
    # try:
    #     deck = Deck.objects.get(pk=deck_id)
    # except Deck.DoesNotExist:
    #     raise Http404("Deck does not exist.")
    deck = get_object_or_404(Deck, pk=deck_id)

    return render(request, 'decks/detail.html', {'deck': deck})


def proxy_maker(request):
    form = CodeInputForm()
    return render(request, 'decks/proxy_maker.html', {
        'form': form,
        "disable_breadcrumb": True,
    })


@login_required()
def proxy_maker_login(request):
    form = CodeInputForm()
    return render(request, 'decks/proxy_maker.html', {
        'form': form,
    })


def proxy_result(request):
    if request.GET.get("type") == "pdf":
        response = dl_img_and_return_http_response(request.GET.get("deck_code"))
    elif request.GET.get("type") == "zip":
        response = dl_img_and_return_zip_http_response(request.GET.get("deck_code"))
    elif request.GET.get("type") == "csv":
        response = generate_csv_and_return_response(request.GET.get("deck_code"))
    else:
        response = Http404

    def get_client_ip(req):
        x_forwarded_for = req.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = req.META.get('REMOTE_ADDR')
        return ip

    deck_code = DeckCode(text=request.GET.get("deck_code"), date=timezone.now(), ip=get_client_ip(request))
    deck_code.save()

    return response


class SearchSubmitView(View):
    def __init__(self):
        super().__init__()
        self.template = 'decks/search_submit.html'
        self.response_message = 'This is the response'

    def post(self, request):
        template = loader.get_template(self.template)
        query = request.POST.get('search', '')

        def a_tag_generator(element: Card):
            return "<a href='" + reverse("decks:card_view", args=[element.global_id_number]) + "'>" + element.name.name + "</a>"

        # A simple query for Item objects whose title contain 'query'
        items = [a_tag_generator(elm) + ", " + elm.set.code for elm in Card.objects.filter(name__name__icontains=query)]
        if not items:
            items = [a_tag_generator(elm) + ", "  + elm.set.code for elm in Card.objects.filter(
                name__name__icontains=romaji2katakana(query))]
        if not items:
            items = [a_tag_generator(elm) + ", "  + elm.set.code for elm in Card.objects.filter(
                name__name__icontains=hiragana2katakana(romaji2katakana(query)))]

        context = {'title': self.response_message, 'query': query, 'items': items}

        rendered_template = template.render(context, request)
        return HttpResponse(rendered_template, content_type='text/html')


class SearchAjaxSubmitView(SearchSubmitView):
    def __init__(self):
        super().__init__()
        self.template = 'decks/search_results.html'
        self.response_message = 'This is the AJAX response'


def card_view(request, card_id):
    card = get_object_or_404(Card, global_id_number=card_id)
    card.fields = dict((field.name, field.value_to_string(card)) for field in card._meta.fields)
    return render(request, "decks/card_view.html", {"card": card})


class NewDeckAjaxView(View):
    def __init__(self):
        super().__init__()
        self.template = 'decks/new_deck_ajax.html'
        self.response_message = 'This is the response'

    def get(self, request):
        template = loader.get_template(self.template)
        deck_id = request.COOKIES.get('deck_id')

        if not deck_id:
            # A simple query for Item objects whose title contain 'query'
            new_deck = Deck(name="新しいデッキ" + str(int(random() * 100)), pub_date=timezone.now(), mod_date=timezone.now(), description="(説明なし)",
                            owner=PTCG2winUser.objects.get(id=request.user.id),
                            regulation=Regulation.objects.get(name="SM以降"),
                            arch_type=ArchType.objects.get_or_create(name="aa",
                                                                     regulation=Regulation.objects.get(name="SM以降"))[0])
            new_deck.save()

            new_deck_list = DeckList(parent_deck=new_deck, deck_code="", created_date=timezone.now())
            new_deck_list.save()

            related_card_bundles = []

            new_card_bundle_1 = CardBundle(card=Card.objects.get(global_id_number=35140), amount=3, parent_deck_list=new_deck_list)
            new_card_bundle_1.save()

            related_card_bundles = CardBundle.objects.filter(parent_deck_list=new_deck_list)
        else:
            new_deck = Deck.objects.get(id=deck_id)
            new_deck_list = DeckList.objects.filter(parent_deck=new_deck).order_by("created_date")[:1]
            related_card_bundles = CardBundle.objects.filter(parent_deck_list=new_deck_list)

        card_bundle_list_str = str([[int(elm.card.global_id_number), elm.amount] for elm in related_card_bundles])
        # print(card_bundle_list_str)

        context = {'title': self.response_message, "deck": new_deck,
                   'deck_list': new_deck_list, "related_card_bundles": related_card_bundles}

        rendered_template = template.render(context, request)

        response = HttpResponse(rendered_template, content_type='text/html')

        set_cookie(response, "deck_id", new_deck.id, 365*24*60*60)
        set_cookie(response, "card_bundles", urllib.parse.quote(card_bundle_list_str), 365 * 24 * 60 * 60)

        return response


def set_cookie(response, key, value, max_age):
    expires = datetime.strftime(datetime.utcnow() + timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
    response.set_cookie(key, value, max_age=max_age, expires=expires)


def card_search_view(request):
    return render(request, 'decks/new_deck.html')

# def search(request, deck_id_from, deck_id_to):
#     return HttpResponse("You are looking from %s to " % deck_id_from + "%s" % deck_id_to)




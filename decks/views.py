from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.template import loader
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django_filters.views import FilterView
from django.utils import timezone

from pure_pagination.mixins import PaginationMixin
from .models import Deck, DeckCode
from .filters import DeckFilter
from .forms import DeckRegisterForm
from .proxy_maker import dl_img_and_return_http_response, dl_img_and_return_zip_http_response, CodeInputForm, generate_csv_and_return_response

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


def index(request):
    latest_deck_list = Deck.objects.order_by('-pub_date')[:5]
    context = {
        'latest_deck_list': latest_deck_list,
        "disable_breadcrumb": True,
    }
    return render(request, 'decks/index.html', context)


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



# def search(request, deck_id_from, deck_id_to):
#     return HttpResponse("You are looking from %s to " % deck_id_from + "%s" % deck_id_to)




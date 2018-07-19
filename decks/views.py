from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.template import loader
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django_filters.views import FilterView

from pure_pagination.mixins import PaginationMixin
from .models import Deck
from .filters import DeckFilter
from .forms import DeckRegisterForm
from .proxy_maker import dl_img_and_return_http_response, dl_img_and_return_zip_http_response, CodeInputForm

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


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


def proxy_maker(request):
    form = CodeInputForm()
    return render(request, 'decks/proxy_maker.html', {
        'form': form,
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
    else:
        response = Http404
    return response


# 検索一覧画面

class DeckFilterView(LoginRequiredMixin, PaginationMixin, FilterView):
    model = Deck
    filterset_class = DeckFilter
    # デフォルトの並び順を新しい順とする
    queryset = Deck.objects.all().order_by('-pub_date')

    # pure_pagination用設定
    paginate_by = 3
    object = Deck

    # 検索条件をセッションに保存する or 呼び出す
    def get(self, request, **kwargs):
        if request.GET:
            request.session['query'] = request.GET
        else:
            request.GET = request.GET.copy()
            if 'query' in request.session.keys():
                for key in request.session['query'].keys():
                    request.GET[key] = request.session['query'][key]

        return super().get(request, **kwargs)


# 詳細画面
class DeckDetailView(LoginRequiredMixin, DetailView):
    model = Deck


# 登録画面
class DeckCreateView(LoginRequiredMixin, CreateView):
    model = Deck
    form_class = DeckRegisterForm
    success_url = reverse_lazy('index')


# 更新画面
class DeckUpdateView(LoginRequiredMixin, UpdateView):
    model = Deck
    form_class = DeckRegisterForm
    success_url = reverse_lazy('index')


# 削除画面
class DeckDeleteView(LoginRequiredMixin, DeleteView):
    model = Deck
    success_url = reverse_lazy('index')


# def search(request, deck_id_from, deck_id_to):
#     return HttpResponse("You are looking from %s to " % deck_id_from + "%s" % deck_id_to)




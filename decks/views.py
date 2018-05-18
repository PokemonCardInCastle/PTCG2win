from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.


def index(request):
    return HttpResponse("ぴよーーーー")


def detail(request, deck_id):
    return HttpResponse("You are looking at deck %s." % deck_id)


# def search(request, deck_id_from, deck_id_to):
#     return HttpResponse("You are looking from %s to " % deck_id_from + "%s" % deck_id_to)




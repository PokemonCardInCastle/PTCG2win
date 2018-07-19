from django.urls import path

from . import views


app_name = 'decks'
urlpatterns = [
    # e.g. /decks/
    path("", views.index, name="index"),
    # e.g. /decks/0/
    path("<int:deck_id>/", views.detail, name="detail"),
    # # e.g. /decks/search/?from=0&to=0
    # path("search/", views.search, name="search"),
    path("proxy_maker", views.proxy_maker, name="proxy_maker"),
    path("proxy_maker_login", views.proxy_maker_login, name="proxy_maker_login"),
    path("proxy_result", views.proxy_result, name="proxy_result")
]

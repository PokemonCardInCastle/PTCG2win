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
]

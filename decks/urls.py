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
    path("deck_board/", views.deck_board, name="deck_board"),

    path("card_post_search/", views.card_search_view, name="post_view"),
    path("card_search/", views.SearchSubmitView.as_view(), name="search-submit"),
    path("card_search_ajax/", views.SearchAjaxSubmitView.as_view(), name="search-ajax-submit"),

    path("new_deck_ajax/", views.NewDeckAjaxView.as_view(), name="deck_edit_ajax"),

    path("proxy_maker/", views.proxy_maker, name="proxy_maker"),
    path("proxy_maker_login/", views.proxy_maker_login, name="proxy_maker_login"),
    path("proxy_result/", views.proxy_result, name="proxy_result"),

    path("cards/<int:card_id>/", views.card_view, name="card_view")
]

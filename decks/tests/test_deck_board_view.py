from django.test import TestCase
from django.urls import reverse
from django.urls import resolve
from decks.views import index, deck_board
from django.utils import timezone


class DeckBoardViewTest(TestCase):
    def setUp(self):
        url = reverse("decks:deck_board")
        self.response = self.client.get(url)

    def test_deck_board_status_code(self):
        url = reverse("decks:deck_board")
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_deck_board_url_resolves_deck_board_view(self):
        view = resolve("/deck_board/")
        self.assertEquals(view.func, deck_board)












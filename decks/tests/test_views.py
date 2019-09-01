from django.test import TestCase
from django.urls import reverse
from django.urls import resolve
from decks.views import index
from decks.models import DeckCode
from django.utils import timezone
from decks.views import proxy_maker

# Create your tests here.


class HomeTests(TestCase):
    def test_home_view_status_code(self):
        url = reverse('decks:index')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_home_url_resolves_home_view(self):
        view = resolve("/")
        self.assertEquals(view.func, index)


class ProxyMakerTests(TestCase):
    def setUp(self):
        DeckCode.objects.create(text="b15FFb-UGLykW-wFV1VF", date=timezone.now(), ip="127.0.0.1")


class CardViewTest(TestCase):
    def test_card_view_status_code(self):
        url = reverse("decks:card_detail_view")
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)





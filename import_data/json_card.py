import json, os, sys
import django

sys.path.append(r"C:\Users\lagyu.DESKTOP-DCLAL1H\PycharmProjects\PTCG2win")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PTCG2win.settings')
django.setup()

from decks.models import *


sets_list = json.load(open('sets\u005CfromXY1.json', 'r'))["sets"]

error_cards = []

for i in range(len(sets_list)):
    set_code_i = sets_list[i]["code"]
    set_cards_list = json.load(open('cards\u005C' + set_code_i + '.json', 'r'))["cards"]

    for card in set_cards_list:
        try:
            _, created = Card.objects.get_or_create(
                artist=card["artist"],
                expansion=Expansion.objects.get(code=set_code_i),  # setと対応
                global_id=card["id"],
                name=card["name"],
                name_j="",
                id_in_expansion=card["number"],
                rarity=Rarity.objects.get_or_create(name=card["rarity"])[0],
                series=Series.objects.get_or_create(name=card["series"])[0],
                is_prism_star=False if card["name"].find("\u25c7") == -1 else True
            )
        except ValueError:
            error_cards.append(card)


print(error_cards)

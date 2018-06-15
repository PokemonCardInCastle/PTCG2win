import json
import os
import sys
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
            if card["supertype"] == "Pok\u00e9mon":
                if card["subtype"] == "Basic":
                    _, created = BasicPokemon.objects.get_or_create(
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
                elif card["subtype"] == "Stage 1":
                    _, created = StageOnePokemon.objects.get_or_create(
                        artist=card["artist"],
                        expansion=Expansion.objects.get(code=set_code_i),  # setと対応
                        global_id=card["id"],
                        name=card["name"],
                        name_j="",
                        id_in_expansion=card["number"],
                        rarity=Rarity.objects.get_or_create(name=card["rarity"])[0],
                        series=Series.objects.get_or_create(name=card["series"])[0],
                        is_prism_star=False if card["name"].find("\u25c7") == -1 else True,
                        evolves_from=card["evolvesFrom"],
                    )


        except ValueError:
            error_cards.append(card)

if error_cards:
    print(error_cards)

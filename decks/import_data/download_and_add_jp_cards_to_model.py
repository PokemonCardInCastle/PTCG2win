from decks.import_data.jp_json_generator import GetCardInfo
import requests
import json
import urllib.parse
import urllib.request
import codecs

import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "../../")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PTCG2win.settings')
django.setup()

from decks.models import *


page = 1
params = {
        "page": page
    }
p = urllib.parse.urlencode(params)
url = "https://www.pokemon-card.com/card-search/resultAPI.php?" + p

page_1_str = requests.get(url).text

page_1_dict = json.loads(page_1_str)

total_page = page_1_dict["maxPage"]
# try:
#     os.mkdir("out1_dir")
# except FileExistsError:
#     pass
#
# try:
#     os.mkdir("out1_dir/data")
# except FileExistsError:
#     pass

for i in range(total_page):
    #     params = {
    #         "page": i + 1
    #     }
    #     p = urllib.parse.urlencode(params)
    print("Started: Page", i)
    url = "https://www.pokemon-card.com/card-search/resultAPI.php?page=" + str(i+1)

    page_str = requests.get(url).text
    page_dict = json.loads(page_str)

    for j in range(len(page_dict["cardList"])):
        global_id_number = int(page_dict["cardList"][j]["cardID"])
        info = GetCardInfo(global_id_number).get_info()
        # print(info)
        if "artist" not in info:
            info.update(artist="Unknown Artist.")

        if info["supertype"] == "Pok\u00e9mon":
            card, created = Pokemon.objects.get_or_create(
                global_id_number=global_id_number,
                defaults=dict(
                    # 共通パート
                    artist=Artist.objects.get_or_create(name=info["artist"])[0],
                    set=Expansion.objects.get(code=info["setCode"]),
                    name=CardName.objects.get_or_create(name=info["name"])[0],
                    id_in_expansion=info["id"] if "id" in info else None,
                    rarity=Rarity.objects.get_or_create(name=info["rarity"])[0] if "rarity" in info else None,
                    supertype=SuperType.objects.get_or_create(name="Pok\u00e9mon", name_j="ポケモン")[0],
                    subtype=SubType.objects.get_or_create(name=info["subtype"],
                                                          name_j=info["subtype"],
                                                          supertype=SuperType.objects.get(name=info["supertype"]))[0],

                    # ここまで共通パート

                    # 以下、ポケモン固有パート
                    hp=int(info["hp"]),
                    retreat_cost=info["convertedRetreatCost"],
                    weakness=None if not info["weaknesses"] else Weakness.objects.get_or_create(name=info["weaknesses"][0]["type"]+info["weaknesses"][0]["value"],
                                                            defaults=dict(
                                                                type=Type.objects.get_or_create(name=info["weaknesses"][0]["type"])[0],
                                                                value=info["weaknesses"][0]["value"]))[0],
                    resistance=None if not info["resistances"] else
                    Resistance.objects.get_or_create(name=info["resistances"][0]["type"] + info["resistances"][0]["value"],
                                                   defaults=dict(
                                                       type=
                                                       Type.objects.get_or_create(name=info["resistances"][0]["type"])[
                                                           0],
                                                       value=info["resistances"][0]["value"]))[0],
                    evolves_from=info["evolvesFrom"],
                    evolution_list_str=str(info["evolution_list_list"])
                )
            )

            if card:
                if "text" in info:
                    for text_str in info["text"]:
                        card.text.add(CardText.objects.get_or_create(name=text_str)[0])

                for type_str in info["types"]:
                    card.types.add(Type.objects.get_or_create(name=type_str)[0])

                if "rarity" in info and info["rarity"] == "Prism Star":
                        card.is_prism_star = True

                if info["attacks"]:
                    for attack in info["attacks"]:
                        Attack.objects.get_or_create(
                            cost=AttackCost.objects.get_or_create(
                                name=",".join(attack["cost"]),
                                convertedEnergyCost=attack["convertedEnergyCost"],
                                grass=attack["cost"].count("Grass"),
                                fire=attack["cost"].count("Fire"),
                                water=attack["cost"].count("Water"),
                                lightning=attack["cost"].count("Lightning"),
                                fighting=attack["cost"].count("Fighting"),
                                colorless=attack["cost"].count("Colorless"),
                                darkness=attack["cost"].count("Darkness"),
                                metal=attack["cost"].count("Metal"),
                                fairly=attack["cost"].count("Fairy"),
                                free=attack["cost"].count("Free"),
                                dragon=attack["cost"].count("Dragon")

                            )[0],
                            damage=attack["damage"],
                            name=attack["name"],
                            text=attack["text"],
                            card=Card.objects.get(global_id_number=global_id_number)
                        )

                if info["abilities"]:
                    for ability in info["abilities"]:
                        Ability.objects.get_or_create(
                            name=ability["name"],
                            text=ability["text"],
                            type=AbilityType.objects.get_or_create(name=ability["type"])[0],
                            card=Card.objects.get(global_id_number=global_id_number)
                        )

        elif info["supertype"] == "Energy" or info["supertype"] == "Trainer":
            card, created = Card.objects.get_or_create(
                global_id_number=global_id_number,
                defaults=dict(
                    # 共通パート
                    artist=Artist.objects.get_or_create(name=info["artist"])[0],
                    set=Expansion.objects.get(code=info["setCode"]),
                    name=CardName.objects.get_or_create(name=info["name"])[0],
                    id_in_expansion=info["id"] if "id" in info else None,
                    rarity=Rarity.objects.get_or_create(name=info["rarity"])[0] if "rarity" in info else None,
                    supertype=SuperType.objects.get_or_create(name=info["supertype"], name_j=info["supertype"])[0],
                    subtype=SubType.objects.get_or_create(
                        name=info["subtype"], name_j=info["subtype"],
                        supertype=SuperType.objects.get(name=info["supertype"]))[0],

                    # ここまで共通パート
                )
            )

            if card:
                if "text" in info:
                    for text_str in info["text"]:
                        card.text.add(CardText.objects.get_or_create(name=text_str)[0])

                if "rarity" in info and info["rarity"] == "Prism Star":
                        card.is_prism_star = True













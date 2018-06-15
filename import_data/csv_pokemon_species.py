import csv
import json
import os
import sys
import django
from time import sleep
import urllib.request
import urllib.parse
import requests
import re


sys.path.append(r"C:\Users\lagyu.DESKTOP-DCLAL1H\PycharmProjects\PTCG2win")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PTCG2win.settings')
django.setup()

from decks.models import *


def title_case(s):
    return re.sub(r"[\w\-]+('[\w\-]+)?",
                  lambda mo: mo.group(0)[0].upper() + mo.group(0)[1:].lower(), s)


pokemon_region_name = ["Kanto", "Johto", "Hoenn", "Sinnoh", "Unova", "Kalos", "Alola"]
pokemon_region_name_j = ["カント―", "ジョウト", "ホウエン", "シンオウ", "イッシュ", "カロス", "アローラ"]


for i in range(len(pokemon_region_name)):

    PokemonRegion.objects.get_or_create(
        name=pokemon_region_name[i],
        name_j=pokemon_region_name_j[i]
    )


with open("PokemonSpeies_utf.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)

    for row in reader:

        _, created = PokemonSpecies.objects.get_or_create(
            name=row[2],
            name_j=row[7],
            pokedex_number=int(row[1]),
            region=PokemonRegion.objects.get(name=row[5])
        )


def collect_evolution_data():
    def collect_individual_evolution_data():
        for chain_elem in chain_list_dict['results']:

            url = chain_elem["url"]

            # print(url)
            sleep(3)

            r = requests.get(url)
            chain_str = r.text.replace("nidoran-f", "Nidoran♀").replace("nidoran-m", "Nidoran♂").replace(
                "mr-mime", "Mr. Mime").replace("mime-jr", "Mime Jr.").replace("flabebe", "Flabébé").replace(
                "type-null", "Type: Null")
            # print(cards_str)
            chain_dict = json.loads(chain_str)
            if "chain" in chain_dict:
                basic_name = title_case(chain_dict["chain"]["species"]["name"])
            else:
                continue

            for evolves_to_elem in chain_dict["chain"]["evolves_to"]:
                print(basic_name, ">", title_case(evolves_to_elem["species"]["name"]))
                PokemonSpecies.objects.filter(name=title_case(evolves_to_elem["species"]["name"])).update(
                    evolves_from=PokemonSpecies.objects.get(name=title_case(basic_name)))

                if "evolves_to" in evolves_to_elem:
                    for evolves_to_2_elem in evolves_to_elem["evolves_to"]:
                        # print(evolves_to_2_elem)
                        PokemonSpecies.objects.filter(name=title_case(evolves_to_2_elem["species"]["name"])).update(
                            evolves_from=PokemonSpecies.objects.get(name=title_case(evolves_to_elem["species"]["name"])))

    # Start main loop
    chain_list_dict = json.loads(requests.get("https://pokeapi.co/api/v2/evolution-chain/?limit=20").text)
    while chain_list_dict["next"]:

        collect_individual_evolution_data()

        sleep(3)
        print("next=", chain_list_dict["next"])
        chain_list_dict = json.loads(requests.get(chain_list_dict["next"]).text)

    # End main loop.
    # Start last loop.
    else:
        collect_individual_evolution_data()
    # End


collect_evolution_data()


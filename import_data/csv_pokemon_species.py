import csv, os, sys
import django

sys.path.append(r"C:\Users\lagyu.DESKTOP-DCLAL1H\PycharmProjects\PTCG2win")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PTCG2win.settings')
django.setup()

from decks.models import *

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


import json, os, sys
import django
from datetime import datetime as dt

sys.path.append(r"C:\Users\lagyu.DESKTOP-DCLAL1H\PycharmProjects\PTCG2win")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PTCG2win.settings')
django.setup()

from decks.models import *

Region.objects.get_or_create(
    name="North America",
    name_j="北アメリカ"
)

with open(r"sets\fromXY1.json", "r", encoding="utf-8") as f:
    reader = json.load(f)
    sets = reader["sets"]

    for expansion in sets:

        _, created = Expansion.objects.get_or_create(
            name=expansion["name"],
            region=Region.objects.get(name="North America"),
            pub_date=dt.strptime(expansion["releaseDate"], "%m/%d/%Y"),
            code=expansion["code"],
            logo_url=expansion["logoUrl"],
            symbol_url=expansion["symbolUrl"],
            total_cards=int(expansion["totalCards"]),
            series=expansion["series"]
        )


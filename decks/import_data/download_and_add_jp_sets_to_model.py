import requests
import re
from bs4 import BeautifulSoup
from decks.import_data.jp_json_generator import DownloadAndSplitHTML

import urllib.parse
import urllib.request
import json
import codecs

import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "../../")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PTCG2win.settings')
django.setup()

from decks.models import *

cards_list = []

Region.objects.get_or_create(
    name="Japan",
    name_j="日本"
)

page = 1
params = {
        "page": page
    }
p = urllib.parse.urlencode(params)
url = "https://www.pokemon-card.com/card-search/resultAPI.php?" + p

page_1_str = requests.get(url).text

page_1_dict = json.loads(page_1_str)

total_page = page_1_dict["maxPage"]
try:
    os.mkdir("sets_out_dir")
except FileExistsError:
    pass

try:
    os.mkdir("sets_out_dir/data")
except FileExistsError:
    pass


class DownloadHTML:
    def __init__(self, card_id: int):
        self.url = "https://www.pokemon-card.com/card-search/details.php/card/" + str(card_id) + "/regu/all"
        self.html = requests.get(self.url).content
        self.card_id = card_id

    def return_html(self):
        return self.html

    def return_return_card_global_id_number(self):
        return self.card_id


for i in range(total_page):
    #     params = {
    #         "page": i + 1
    #     }
    #     p = urllib.parse.urlencode(params)
    print("Started: Page", i)
    url = "https://www.pokemon-card.com/card-search/resultAPI.php?page=" + str(i+1)

    page_str = requests.get(url).text
    page_dict = json.loads(page_str)

    f = codecs.open(r"sets_out_dir/data/page_" + str(i) + ".json", "w", "utf-8")
    json.dump(page_dict, f, sort_keys=True, indent=4)
    f.close()

    for j in range(len(page_dict["cardList"])):
        global_id_number = int(page_dict["cardList"][j]["cardID"])

        html_class = DownloadHTML(global_id_number)

        soup = BeautifulSoup(html_class.return_html(), "lxml")

        img_regulation_tag = soup.find("img", class_="img-regulation")
        if img_regulation_tag:
            setCode = img_regulation_tag.get("alt")
            symbol_url = "https://www.pokemon-card.com" + img_regulation_tag.get("src")

            item, created = Expansion.objects.get_or_create(
                code=setCode,
                defaults=dict(
                    region=Region.objects.get(name="Japan"),
                    pub_date=None,
                    name="新規",
                    logo_url=None,
                    symbol_url=symbol_url,
                    info_url="",
                    total_cards=None,
                    series=None
                )
            )
        else:
            continue

        if item:
            if item.info_url == "":
                info_a_tag = soup.find("a", class_="Link Link-arrow")
                if info_a_tag:
                    item.info_url = info_a_tag.get("href") if "://www.pokemon-card.com" in info_a_tag.get("href") \
                        else "https://www.pokemon-card.com" + info_a_tag.get("href")
                    if item.name == "新規":
                        item.name = info_a_tag.text.replace("\n", "").replace("\t", "")
                    item.save()
                else:
                    pass

        if created:
            if item.info_url == "":
                info_a_tag = soup.find("a", class_="Link Link-arrow")
                if info_a_tag:
                    created.info_url = info_a_tag.get("href") if "://www.pokemon-card.com" in info_a_tag.get("href") \
                        else "https://www.pokemon-card.com" + info_a_tag.get("href")
                    if item.name == "新規":
                        created.name = info_a_tag.text.replace("\n", "").replace("\t", "")

                    created.save()
                else:
                    pass






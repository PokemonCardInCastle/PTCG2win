from decks.import_data.jp_json_generator import GetCardInfo
import requests
import json
import urllib.parse
import urllib.request
import codecs
import os



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
    os.mkdir("out1_dir")
except FileExistsError:
    pass

try:
    os.mkdir("out1_dir/data")
except FileExistsError:
    pass

for i in range(total_page):
    #     params = {
    #         "page": i + 1
    #     }
    #     p = urllib.parse.urlencode(params)
    print("Started: Page", i)
    url = "https://www.pokemon-card.com/card-search/resultAPI.php?page=" + str(i+1)

    page_str = requests.get(url).text
    page_dict = json.loads(page_str)

    f = codecs.open(r"out1_dir/data/page_" + str(i) + ".json", "w", "utf-8")
    json.dump(page_dict, f, sort_keys=True, indent=4)
    f.close()

    for j in range(len(page_dict["cardList"])):
        global_id_number = int(page_dict["cardList"][j]["cardID"])
        info = GetCardInfo(global_id_number).get_info()
        # print(info)

        f = codecs.open(r"out1_dir/" + page_dict["cardList"][j]["cardID"]+".json", "w", "utf-8")
        json.dump(info, f, sort_keys=True, indent=4)
        f.close()






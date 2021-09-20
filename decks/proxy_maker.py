import io
from typing import List

from PIL import Image, ImageChops
from reportlab.lib.utils import ImageReader
import requests
from bs4 import BeautifulSoup
import re
from django.http import HttpResponse, FileResponse
from django import forms
import zipfile
import csv
from io import BytesIO
from fpdf import FPDF


class CodeInputForm(forms.Form):
    deck_code = forms.CharField(max_length=20,
                                min_length=20,
                                label="デッキコード",
                                widget=forms.TextInput(
                                    attrs={'class': 'form-control mr-4',
                                           "type": "text",
                                           'placeholder': '例：c4c8Jx-8aVtOj-cYxcax'}))
    type = forms.ChoiceField(choices=(("pdf", "pdf"), ("zip", "zip")),
                             label="ファイルタイプ",
                             initial="pdf",
                             widget=forms.RadioSelect(
                                 attrs={'class': 'btn btn-primary',
                                        "type": "text",
                                        })
                             )


def fetch_images_and_return_response(deck_code: str):
    code = deck_code
    file_name = deck_code

    # html = requests.get("https://www.pokemon-card.com/deck/deck.html?deckID=11F1Fw-VNG8m4-fk1bVF").content
    html = requests.get("https://www.pokemon-card.com/deck/deck.html?deckID=" + code).content

    soup = BeautifulSoup(html, "html.parser")

    card_data_script_text = soup.find_all("script")[-1].contents[0]

    # deck_pke_list の例: [["33525", "3"], ["33525", "3"]]
    deck_pke_list = [elem.split("_")[:2] for elem in soup.find(id="deck_pke")["value"].split("-")]
    deck_gds_list = [elem.split("_")[:2] for elem in soup.find(id="deck_gds")["value"].split("-")] \
        if soup.find(id="deck_gds")["value"] != "" else []
    deck_sup_list = [elem.split("_")[:2] for elem in soup.find(id="deck_sup")["value"].split("-")] \
        if soup.find(id="deck_sup")["value"] != "" else []
    deck_sta_list = [elem.split("_")[:2] for elem in soup.find(id="deck_sta")["value"].split("-")] \
        if soup.find(id="deck_sta")["value"] != "" else []
    deck_ene_list = [elem.split("_")[:2] for elem in soup.find(id="deck_ene")["value"].split("-")] \
        if soup.find(id="deck_ene")["value"] != "" else []
    # deck_ajs_list = [elem.split("_")[:2] for elem in soup.find(id="deck_ajs")["value"].split("-")]\
    #     if soup.find(id="deck_ajs")["value"] != "" else []

    deck_list = deck_pke_list + deck_gds_list + deck_sup_list + deck_sta_list + deck_ene_list  # + deck_ajs_list
    cards_to_print_count = 0

    card_url_list = []

    dl_counter = 0

    for elm in deck_list:
        dl_counter += 1
        pattern = re.compile(r"(/assets/images/card_images/([a-zA-Z]+)/[^\n]*/0+%s_[^\n]+\.jpg)" % elm[0],
                             re.MULTILINE | re.DOTALL)
        match = pattern.search(card_data_script_text)

        if match:
            url = "https://www.pokemon-card.com" + match.group(1)
            elm.append(url)
        #    print(elm)
        else:
            # たまに画像がなくて裏面の画像なことがあるので、その対応
            url = "https://www.pokemon-card.com/assets/images/noimage/poke_ura.jpg"
            elm.append(url)

        try:
            for i in range(int(elm[1])):
                cards_to_print_count += 1
                card_url_list.append(elm[2])
        except ValueError:
            return HttpResponse(
                "デッキコードが正しくないか、ポケモンカード公式のサーバが応答していません。",
                content_type="text/plain; charset=utf-8"
            )

    # キャンバスと出力ファイルの初期化
    pdf = FPDF(orientation='P', unit='mm', format="A4")

    pdf.set_author("PTCG2Win")
    pdf.set_title(deck_code)
    pdf.set_subject("PDF to print")

    card_url_or_image_list = []

    def split_images_and_append_to_list(input_image: Image.Image, x_pieces, y_pieces, output_list):
        imgwidth, imgheight = input_image.size
        height = imgheight // y_pieces
        width = imgwidth // x_pieces
        for j in range(y_pieces):
            for k in range(x_pieces):
                box = (k * width, j * height, (k + 1) * width, (j + 1) * height)
                part = input_image.crop(box)
                output_list.append(part)

    def trim(input_image: Image.Image) -> Image.Image:
        bg = Image.new(input_image.mode, input_image.size, input_image.getpixel((0, 0)))
        diff = ImageChops.difference(input_image, bg)
        diff = ImageChops.add(diff, diff, 2.0, -100)
        bbox = diff.getbbox()
        if bbox:
            return input_image.crop(bbox)

    v_union_filename_pattern: re.Pattern = re.compile(r"[A-Z]VUNION\.jpg$")
    reduced_card_url_list = []
    cards_count = len(card_url_list)
    for i in range(cards_count):
        card_url = card_url_list[i]
        if re.search(v_union_filename_pattern, card_url):
            for j in range(card_url_list.count(card_url) // 4):
                reduced_card_url_list.append(card_url)
            card_url_list = ["" if url == card_url else url for url in card_url_list]
        else:
            reduced_card_url_list.append(card_url)
    filtered_card_url_list = [card_url for card_url in reduced_card_url_list if card_url != ""]

    for card_url in filtered_card_url_list:
        if "/card_images/legend/" in card_url:
            rsp = requests.get(card_url, stream=True)
            rsp.raw.decode_content = True
            img_object = Image.open(rsp.raw)
            img_object = img_object.rotate(90, expand=True)
            card_url_or_image_list.append(img_object)
        elif re.search(v_union_filename_pattern, card_url):
            rsp = requests.get(card_url, stream=True)
            rsp.raw.decode_content = True
            img_object = trim(Image.open(rsp.raw))
            split_images_and_append_to_list(img_object, 2, 2, card_url_or_image_list)
        else:
            card_url_or_image_list.append(card_url)

    # ポケモンカードのサイズは63x88なので、紙を縦置きにした場合、3枚x3枚(189x264)入る。
    for i in range(len(card_url_or_image_list)):
        card_url_or_image = card_url_or_image_list[i]
        # 9枚ごとに改ページ
        if i % 9 == 0:
            pdf.add_page("P")
        #        print("Page", i // 9 + 1)
        # 3枚ごとに改行
        x_pos = (11 + 63 * (i % 3))
        y_pos = (15 + 88 * ((i % 9) // 3))

        pdf.image(
            card_url_or_image,
            x_pos,
            y_pos,
            w=63,
            h=88,
        )

    buffer = BytesIO()

    output = pdf.output()
    buffer.write(output)
    buffer.seek(0)
    # httpレスポンスの作成
    return FileResponse(buffer, filename=f"{deck_code}.pdf", as_attachment=True, content_type='application/pdf')


def generate_csv_and_return_response(deck_code: str):
    code = deck_code
    file_name = deck_code

    # html = requests.get("https://www.pokemon-card.com/deck/deck.html?deckID=11F1Fw-VNG8m4-fk1bVF").content
    html = requests.get("https://www.pokemon-card.com/deck/deck.html?deckID=" + code).content

    soup = BeautifulSoup(html, "html.parser")

    card_data_script_text = soup.find_all("script")[-1].contents[0]

    # deck_pke_list の例: [["33525", "3"], ["33525", "3"]]
    deck_pke_list = [elem.split("_")[:2] for elem in soup.find(id="deck_pke")["value"].split("-")]
    deck_gds_list = [elem.split("_")[:2] for elem in soup.find(id="deck_gds")["value"].split("-")] \
        if soup.find(id="deck_gds")["value"] != "" else []
    deck_sup_list = [elem.split("_")[:2] for elem in soup.find(id="deck_sup")["value"].split("-")] \
        if soup.find(id="deck_sup")["value"] != "" else []
    deck_sta_list = [elem.split("_")[:2] for elem in soup.find(id="deck_sta")["value"].split("-")] \
        if soup.find(id="deck_sta")["value"] != "" else []
    deck_ene_list = [elem.split("_")[:2] for elem in soup.find(id="deck_ene")["value"].split("-")] \
        if soup.find(id="deck_ene")["value"] != "" else []
    # deck_ajs_list = [elem.split("_")[:2] for elem in soup.find(id="deck_ajs")["value"].split("-")]\
    #     if soup.find(id="deck_ajs")["value"] != "" else []

    deck_content_lists_list = [deck_pke_list, deck_gds_list, deck_sup_list, deck_sta_list, deck_ene_list]

    csv_header_row = ["種類", "名前", "枚数", "エキスパンション", "コレクションID", "URL", code]

    csv_content_rows = []

    def get_card_info_dict(card_id_str: str):
        res = requests.get("https://www.pokemon-card.com/deck/deckThumbsImage.php?cardID=" + card_id_str)
        card_info_dict = res.json()
        return card_info_dict

    for i in range(len(deck_content_lists_list)):
        for j in range(len(deck_content_lists_list[i])):
            card_info = get_card_info_dict(deck_content_lists_list[i][j][0])
            categories = ["ポケモン", "グッズ", "サポート", "スタジアム", "エネルギー"]
            csv_content_rows.append(
                [categories[i], card_info["cardName"], deck_content_lists_list[i][j][1], card_info["blockCode"],
                 card_info["collectionCode"],
                 "https://www.pokemon-card.com/card-search/details.php/card/" + card_info["cardID"] + "/"])

    # httpレスポンスの作成
    response = HttpResponse(content_type='application/csv', charset="utf-8")
    response['Content-Disposition'] = 'attachment; filename="' + deck_code + '.csv"'

    response.write('\ufeff')

    writer = csv.writer(response, lineterminator='\n')  # 改行コード（\n）を指定しておく
    writer.writerow(csv_header_row)
    writer.writerows(csv_content_rows)

    # レスポンスを返す
    return response

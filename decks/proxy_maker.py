import time
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import requests
from bs4 import BeautifulSoup
import re
import os
import shutil
import random
from django.http import HttpResponse
from django import forms
from io import BytesIO
import zipfile
import csv
from reportlab.lib.pagesizes import A4
import io
from PIL import Image


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


def dl_img_and_return_http_response(deck_code: str):
    code = deck_code
    file_name = deck_code

    # html = requests.get("https://www.pokemon-card.com/deck/deck.html?deckID=11F1Fw-VNG8m4-fk1bVF").content
    html = requests.get("https://www.pokemon-card.com/deck/deck.html?deckID=" + code).content

    soup = BeautifulSoup(html, "html.parser")

    card_data_script_text = soup.find_all("script")[-1].text

    # deck_pke_list の例: [["33525", "3"], ["33525", "3"]]
    deck_pke_list = [elem.split("_")[:2] for elem in soup.find(id="deck_pke")["value"].split("-")]
    deck_gds_list = [elem.split("_")[:2] for elem in soup.find(id="deck_gds")["value"].split("-")]\
        if soup.find(id="deck_gds")["value"] != "" else []
    deck_sup_list = [elem.split("_")[:2] for elem in soup.find(id="deck_sup")["value"].split("-")]\
        if soup.find(id="deck_sup")["value"] != "" else []
    deck_sta_list = [elem.split("_")[:2] for elem in soup.find(id="deck_sta")["value"].split("-")]\
        if soup.find(id="deck_sta")["value"] != "" else []
    deck_ene_list = [elem.split("_")[:2] for elem in soup.find(id="deck_ene")["value"].split("-")]\
        if soup.find(id="deck_ene")["value"] != "" else []
    # deck_ajs_list = [elem.split("_")[:2] for elem in soup.find(id="deck_ajs")["value"].split("-")]\
    #     if soup.find(id="deck_ajs")["value"] != "" else []

    deck_list = deck_pke_list + deck_gds_list + deck_sup_list + deck_sta_list + deck_ene_list  #+ deck_ajs_list
    cards_to_print_count = 0

    card_url_list = []
    card_img_object_dict = {}

    def download_image_and_return_pil_object(img_url):
        if img_url in card_img_object_dict:
            return card_img_object_dict[img_url]
        else:
            rsp = requests.get(img_url, stream=True)
            rsp.raw.decode_content = True
            img_object = Image.open(rsp.raw)
            if "/legend/" in img_url:
                img_object.rotate(90, expand=True)
            card_img_object_dict[img_url] = img_object
            return img_object

    dl_counter = 0

    for elm in deck_list:
        dl_counter += 1
        pattern = re.compile(r"]='(/assets/images/card_images/(large|legend)/[^\n]+/0+%s_[^\n]+\.jpg)'" % elm[0],
                             re.MULTILINE | re.DOTALL)
        match = pattern.search(card_data_script_text)

        if match:
            url = "http://www.pokemon-card.com" + match.group(1)
            elm.append(url)
    #    print(elm)
        else:
            # たまに画像がなくて裏面の画像なことがあるので、その対応
            url = "http://www.pokemon-card.com/assets/images/noimage/poke_ura.jpg"
            elm.append(url)

        for i in range(int(elm[1])):
            cards_to_print_count += 1
            card_url_list.append(elm[2])

    # httpレスポンスの作成
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="' + deck_code + '.pdf"'

    # キャンバスと出力ファイルの初期化
    pdf_made = canvas.Canvas(response, pagesize=A4)
    pdf_made.saveState()

    pdf_made.setAuthor('PTCG2win')
    pdf_made.setTitle(deck_code)
    pdf_made.setSubject("PDF to print")

    # ポケモンカードのサイズは63x88なので、紙を縦置きにした場合、3枚x3枚(189x264)入る。
    num_card = cards_to_print_count
    # print("Page 1")
    for i in range(num_card):
        # 9枚ごとに改ページ
        if i != 0 and i % 9 == 0:
            pdf_made.showPage()
    #        print("Page", i // 9 + 1)
        # 3枚ごとに改行
        x_pos = (11 + 63 * (i % 3)) * mm
        y_pos = (15 + 88 * ((i % 9) // 3)) * mm
        pdf_made.drawInlineImage(
                                  download_image_and_return_pil_object(card_url_list[i]),
                                  x_pos,
                                  y_pos,
                                  width=63 * mm,
                                  height=88 * mm,
                                  )
    # print("PDF生成中...")
    pdf_made.save()

    # レスポンスを返す
    return response

    # 削除する場合は下のコメントアウトを外す。(キャッシュが効くので削除しないことを推奨)
    # shutil.rmtree("./" + temp_dir_name)

    # print("終了！")


def generate_csv_and_return_response(deck_code: str):
    code = deck_code
    file_name = deck_code

    # html = requests.get("https://www.pokemon-card.com/deck/deck.html?deckID=11F1Fw-VNG8m4-fk1bVF").content
    html = requests.get("https://www.pokemon-card.com/deck/deck.html?deckID=" + code).content

    soup = BeautifulSoup(html, "html.parser")

    card_data_script_text = soup.find_all("script")[-1].text

    # deck_pke_list の例: [["33525", "3"], ["33525", "3"]]
    deck_pke_list = [elem.split("_")[:2] for elem in soup.find(id="deck_pke")["value"].split("-")]
    deck_gds_list = [elem.split("_")[:2] for elem in soup.find(id="deck_gds")["value"].split("-")]\
        if soup.find(id="deck_gds")["value"] != "" else []
    deck_sup_list = [elem.split("_")[:2] for elem in soup.find(id="deck_sup")["value"].split("-")]\
        if soup.find(id="deck_sup")["value"] != "" else []
    deck_sta_list = [elem.split("_")[:2] for elem in soup.find(id="deck_sta")["value"].split("-")]\
        if soup.find(id="deck_sta")["value"] != "" else []
    deck_ene_list = [elem.split("_")[:2] for elem in soup.find(id="deck_ene")["value"].split("-")]\
        if soup.find(id="deck_ene")["value"] != "" else []
    # deck_ajs_list = [elem.split("_")[:2] for elem in soup.find(id="deck_ajs")["value"].split("-")]\
    #     if soup.find(id="deck_ajs")["value"] != "" else []

    deck_content_lists_list = [deck_pke_list, deck_gds_list, deck_sup_list, deck_sta_list, deck_ene_list]

    csv_header_row = ["種類", "名前", "枚数", "エキスパンション", "コレクションID",  "URL", code]

    csv_content_rows = []

    def get_card_info_dict(card_id_str: str):
        res = requests.get("https://www.pokemon-card.com/deck/deckThumbsImage.php?cardID=" + card_id_str)
        card_info_dict = res.json()
        return card_info_dict

    for i in range(len(deck_content_lists_list)):
        for j in range(len(deck_content_lists_list[i])):
            card_info = get_card_info_dict(deck_content_lists_list[i][j][0])
            categories = ["ポケモン", "グッズ", "サポート", "スタジアム", "エネルギー"]
            csv_content_rows.append([categories[i], card_info["cardName"],  deck_content_lists_list[i][j][1], card_info["blockCode"], card_info["collectionCode"], "https://www.pokemon-card.com/card-search/details.php/card/" + card_info["cardID"] + "/"])

    # csv_output_dir_name = "_csv_out"
    # try:
    #     os.mkdir(csv_output_dir_name)
    # except FileExistsError:
    #     pass

    # httpレスポンスの作成
    response = HttpResponse(content_type='application/csv', charset="utf-8")
    response['Content-Disposition'] = 'attachment; filename="' + deck_code + '.csv"'

    response.write('\ufeff')

    writer = csv.writer(response, lineterminator='\n')  # 改行コード（\n）を指定しておく
    writer.writerow(csv_header_row)
    writer.writerows(csv_content_rows)

    # with open("./" + csv_output_dir_name + "/" + code + ".csv", 'w') as f:
    #     writer = csv.writer(f, lineterminator='\n')  # 改行コード（\n）を指定しておく
    #     writer.writerow(csv_header_row)
    #     writer.writerows(csv_content_rows)

    # レスポンスを返す
    return response

    # 削除する場合は下のコメントアウトを外す。(キャッシュが効くので削除しないことを推奨)
    # shutil.rmtree("./" + temp_dir_name)

    # print("終了！")


def dl_img_and_return_zip_http_response(deck_code: str):
    code = deck_code
    if len(code) != 20:
        return HttpResponse("The code you put '" + code + "' is not a valid deck code.")

    file_name = deck_code

    # html = requests.get("https://www.pokemon-card.com/deck/deck.html?deckID=11F1Fw-VNG8m4-fk1bVF").content
    html = requests.get("https://www.pokemon-card.com/deck/deck.html?deckID=" + code).content

    soup = BeautifulSoup(html, "html.parser")

    card_data_script_text = soup.find_all("script")[-1].text

    # deck_pke_list の例: [["33525", "3"], ["33525", "3"]]
    deck_pke_list = [elem.split("_")[:2] for elem in soup.find(id="deck_pke")["value"].split("-")]
    deck_gds_list = [elem.split("_")[:2] for elem in soup.find(id="deck_gds")["value"].split("-")]\
        if soup.find(id="deck_gds")["value"] != "" else []
    deck_sup_list = [elem.split("_")[:2] for elem in soup.find(id="deck_sup")["value"].split("-")]\
        if soup.find(id="deck_sup")["value"] != "" else []
    deck_sta_list = [elem.split("_")[:2] for elem in soup.find(id="deck_sta")["value"].split("-")]\
        if soup.find(id="deck_sta")["value"] != "" else []
    deck_ene_list = [elem.split("_")[:2] for elem in soup.find(id="deck_ene")["value"].split("-")]\
        if soup.find(id="deck_ene")["value"] != "" else []
    # deck_ajs_list = [elem.split("_")[:2] for elem in soup.find(id="deck_ajs")["value"].split("-")]\
    #     if soup.find(id="deck_ajs")["value"] != "" else []

    deck_list = deck_pke_list + deck_gds_list + deck_sup_list + deck_sta_list + deck_ene_list  # + deck_ajs_list
    cards_to_print_count = 0

    card_url_list = []
    card_img_object_dict = {}

    def download_image_and_return_pil_object(img_url):
        if img_url in card_img_object_dict:
            return card_img_object_dict[img_url]
        else:
            rsp = requests.get(img_url, stream=True)
            rsp.raw.decode_content = True
            img_object = Image.open(rsp.raw)
            if "/legend/" in img_url:
                img_object.transpose(Image.ROTATE_90)
            card_img_object_dict[img_url] = img_object
            return img_object

    dl_counter = 0

    for elm in deck_list:
        dl_counter += 1
        pattern = re.compile(r"]='(/assets/images/card_images/(large|legend)/[^\n]+/0+%s_[^\n]+\.jpg)'" % elm[0],
                             re.MULTILINE | re.DOTALL)
        match = pattern.search(card_data_script_text)

        if match:
            url = "http://www.pokemon-card.com" + match.group(1)
            elm.append(url)
        #    print(elm)
        else:
            # たまに画像がなくて裏面の画像なことがあるので、その対応
            url = "http://www.pokemon-card.com/assets/images/noimage/poke_ura.jpg"
            elm.append(url)

        for i in range(int(elm[1])):
            cards_to_print_count += 1
            card_url_list.append(elm[2])

    # httpレスポンスの作成
    response = HttpResponse(content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="' + deck_code + '.zip"'

    # zipfileオブジェクト生成
    pdf_zip = zipfile.ZipFile(response, "w")

    # 1つ目のPDFファイル
    memory_file = BytesIO()

    # キャンバスと出力ファイルの初期化
    pdf_in_memory = canvas.Canvas(memory_file)
    pdf_in_memory.saveState()

    # A4サイズに設定(JIS規格の紙の大きさ。実際の印刷範囲は10mm四方短い190x277程度だと思われる)
    pdf_width = 210.0*mm
    pdf_height = 297.0*mm
    pdf_in_memory.setPageSize((pdf_width, pdf_height))

    # ポケモンカードのサイズは63x88なので、紙を縦置きにした場合、3枚x3枚(189x264)入る。
    num_card = cards_to_print_count
    # print("Page 1")
    for i in range(num_card):
        # 9枚ごとに改ページ
        if i != 0 and i % 9 == 0:
            # ページ終了処理
            pdf_in_memory.showPage()
            # PDF生成
            pdf_in_memory.save()
            # zipfile(response)に書き込み
            pdf_zip.writestr(deck_code + "_page" + str((i // 9)) + ".pdf", memory_file.getvalue())

            ##################################################

            # 新しいpdfを作成
            memory_file = BytesIO()

            # キャンバスと出力ファイルの初期化
            pdf_in_memory = canvas.Canvas(memory_file)
            pdf_in_memory.saveState()

            # A4サイズに設定(JIS規格の紙の大きさ。実際の印刷範囲は10mm四方短い190x277程度だと思われる)
            pdf_width = 210.0 * mm
            pdf_height = 297.0 * mm
            pdf_in_memory.setPageSize((pdf_width, pdf_height))

        #        print("Page", i // 9 + 1)
        # 3枚ごとに改行
        x_pos = (11 + 63 * (i % 3)) * mm
        y_pos = (15 + 88 * ((i % 9) // 3)) * mm
        pdf_in_memory.drawInlineImage(
                                  download_image_and_return_pil_object(card_url_list[i]),
                                  x_pos,
                                  y_pos,
                                  width=63 * mm,
                                  height=88 * mm,
                                  )
    else:
        if i % 9 != 0:
        # ページ終了処理
            pdf_in_memory.showPage()
            # PDF生成
            pdf_in_memory.save()
            # zipfile(response)に書き込み
            pdf_zip.writestr(deck_code + "_page" + str((i // 9) + 1) + ".pdf", memory_file.getvalue())

    pdf_zip.close()

    # レスポンスを返す
    return response

    # 削除する場合は下のコメントアウトを外す。(キャッシュが効くので削除しないことを推奨)
    # shutil.rmtree("./" + temp_dir_name)

    # print("終了！")


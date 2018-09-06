# coding: UTF-8
from html.parser import HTMLParser
from bs4 import BeautifulSoup
from collections import Counter
import lxml

type_list = ["Grass", "Fire", "Water", "Lightning", "Fighting", "Psychic", "Colorless", "Darkness", "Metal", "Dragon",
             "Fairy", "Free"]
type_tag_list = ["grass", "fire", "water", "electric", "fighting", "psychic", "none", "dark", "steel", "dragon",
                 "fairy", "void"]


class SpanTagsHTMLStrToTypeStrList(HTMLParser):
    def error(self, message):
        pass

    def __init__(self):
        HTMLParser.__init__(self)
        self._result = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "span" and "class" in attrs and "icon-" in attrs["class"]:
            class_name_list = attrs["class"].split(" ")
            type_result = self.find_formal_type_str_from_class_name_list(class_name_list)
            # print(type_result)
            self._result.append(type_result)

    def get_type_list(self):
        return self._result

    @staticmethod
    def find_formal_type_str_from_class_name_list(class_name_list: str):
        for class_name in class_name_list:
            for i in range(len(type_tag_list)):
                if type_tag_list[i] in class_name:
                    return type_list[i]
        else:
            raise ValueError("Found no valid type from " + str(class_name_list))


class GetMoveInfoFromTag:
    def __init__(self, move_cost_list_getter):
        self.move_name = ""
        self.move_cost_list_getter = move_cost_list_getter
        self.move_cost_list = []
        self.soup = None
        self.h4soup = None
        self.move_html_h4_str_list = []
        self.move_html_h4_tag_list = []
        self.move_html_p_tag_list = []
        self.attack = {}
        self.attacks = []

    def feed(self, right_box_inner_html_str):
        self.soup = BeautifulSoup(right_box_inner_html_str, "lxml")
        self.move_html_h4_tag_list = self.soup.find_all("h4")
        self.move_html_p_tag_list = self.soup.find_all("p")
        self.move_html_h4_str_list = [str(elem) for elem in self.move_html_h4_tag_list]

        for html_str in self.move_html_h4_str_list:
            self.move_cost_list_getter.__init__()
            self.move_cost_list_getter.feed(html_str)
            self.move_cost_list = self.move_cost_list_getter.get_type_list()
            self.attack.update(cost=self.move_cost_list)

            attack_name = self.move_html_h4_tag_list[self.move_html_h4_str_list.index(html_str)].text.replace(
                "".join([elm1.text for elm1 in BeautifulSoup(html_str, "lxml").find_all("span")]), "").replace(" ",
                                                                                                               "").replace(
                "\xa0", "")

            self.attack.update(name=attack_name)
            self.attack.update(damage="".join([elm1.text for elm1 in BeautifulSoup(html_str, "lxml").find_all("span")]))

            self.attack.update(text=self.move_html_p_tag_list[self.move_html_h4_str_list.index(html_str)].text)

            self.attack.update(convertedEnergyCost=len(self.move_cost_list) - Counter(self.move_cost_list)["Free"])

            self.attacks.append(self.attack.copy())

        print(self.attacks)


class GetWeaknessAndResistanceAndRetreatCost:
    def __init__(self, move_cost_list_getter):
        self.move_cost_list_getter = move_cost_list_getter
        self.weaknesses = []
        self.resistances = []
        self.table_soup = None
        self.move_html_td_tag_list = None
        self.move_html_td_str_list = None
        self.retreat_cost = []
        self.attack = {}
        self.attacks = []
        self._result = {}

    def feed(self, table_html_str):
        self.table_soup = BeautifulSoup(table_html_str, "lxml")
        self.move_html_td_tag_list = self.table_soup.find_all("td")
        self.move_html_td_str_list = [str(elem) for elem in self.move_html_td_tag_list]

        self.move_cost_list_getter.__init__()
        self.move_cost_list_getter.feed(self.move_html_td_str_list[0])
        for type_str in self.move_cost_list_getter.get_type_list():
            self.weaknesses.append({"type": type_str, "value": self.move_html_td_tag_list[0].text})
        self._result.update(weaknesses=self.weaknesses)

        self.move_cost_list_getter.__init__()
        self.move_cost_list_getter.feed(self.move_html_td_str_list[1])
        for type_str in self.move_cost_list_getter.get_type_list():
            self.resistances.append({"type": type_str, "value": self.move_html_td_tag_list[1].text})
        self._result.update(resistances=self.resistances)

        self.move_cost_list_getter.__init__()
        self.move_cost_list_getter.feed(self.move_html_td_str_list[2])
        for type_str in self.move_cost_list_getter.get_type_list():
            self.retreat_cost.append(type_str)
        self._result.update(retreatCost=self.retreat_cost)

    def get_value(self):
        # print(self._result)
        return self._result


class GetPokemonInfo:
    def __init__(self, move_cost_list_getter):
        self.move_cost_list_getter = move_cost_list_getter
        self.name = None
        self.subtype = None
        self.supertype = "Pok\u00e9mon"
        self.types = []
        self.topinfo_soup = None
        self.move_html_td_tag_list = None
        self.move_html_td_str_list = None
        self.retreat_cost = []
        self.attack = {}
        self.attacks = []
        self._result = {}

    def feed(self, topinfo_html_str):
        pass


    # def handle_starttag(self, tag, attrs):
    #     if tag == "h4":
    #         # print(attrs)
    #         print(self.rawdata)
    #         self.move_cost_list_getter.feed(self.get_starttag_text())
    #         self.move_cost_list = self.move_cost_list_getter.get_type_list()
    #         print(self.move_cost_list)
    #         self.move_name_switch = True
    #
    # def handle_data(self, data):
    #     if self.move_name_switch:
    #         self.move_name = data
    #         print(data)
    #         self.move_name_switch = False


if __name__ == '__main__':
    move_cost_list_getter_1 = SpanTagsHTMLStrToTypeStrList()
    test = GetWeaknessAndResistanceAndRetreatCost(move_cost_list_getter_1)
    test.feed(
        r' <div class="TopInfo Text-fjalla"> <div class="tr"> <div class="td-l"> <span class="type">2&nbsp;進化</span> </div> <div class="td-r"> <span class="hp">HP</span> <span class="hp-num">240</span> <span class="hp-type">タイプ</span> <span class="icon-grass icon"></span> </div> </div> </div><h2 class="mt20">ワザ</h2><h4><span class="icon-grass icon"></span>まどわす <span class="f_right Text-fjalla">40</span></h4><p>相手のバトルポケモンをこんらんにする。</p><h4><span class="icon-grass icon"></span><span class="icon-none icon"></span><span class="icon-none icon"></span>じんつうりき <span class="f_right Text-fjalla">90＋</span></h4><p>自分の手札と相手の手札が同じ枚数なら、90ダメージ追加。</p><h2 class="mt20">GXワザ</h2><h4><span class="icon-grass icon"></span><span class="icon-none icon"></span><span class="icon-none icon"></span>ふくまでんGX &nbsp;</h4><p>相手のポケモン1匹と、ついているすべてのカードを、相手の山札にもどして切る。［対戦中、自分はGXワザを1回しか使えない。］</p><h2 class="mt20">特別なルール</h2><p>ポケモンGXがきぜつしたとき、相手はサイドを2枚とる。</p> <table cellspacing="0" cellpadding="0"> <tbody><tr> <th>弱点</th> <th>抵抗力</th> <th>にげる</th> </tr> <tr> <td><span class="icon-fire icon"></span>×2</td> <td>--</td> <td class="escape"><span class="icon-none icon"></span><span class="icon-none icon"></span></td> </tr> </tbody></table> <h2 class="mt20">進化</h2><div class="evolution evbox"><div class="in-box ev_on"><a href="/card-search/index.php?regulation_detail=XY&amp;pokemon=%E3%83%80%E3%83%BC%E3%83%86%E3%83%B3%E3%82%B0GX">ダーテングGX</a></div><div class="in-box ev_off"><a href="/card-search/index.php?regulation_detail=XY&amp;pokemon=%E3%83%80%E3%83%BC%E3%83%86%E3%83%B3%E3%82%B0">ダーテング</a></div></div><div class="evolution ev_off"><a href="/card-search/index.php?regulation_detail=XY&amp;pokemon=%E3%82%B3%E3%83%8E%E3%83%8F%E3%83%8A">コノハナ</a><div class="arrow_off"></div></div><div class="evolution ev_off"><a href="/card-search/index.php?regulation_detail=XY&amp;pokemon=%E3%82%BF%E3%83%8D%E3%83%9C%E3%83%BC">タネボー</a><div class="arrow_off"></div></div> <span class="Text-annotation mt10">「進化」はスタンダードレギュレーションのものです </span> ')
    test.get_value()



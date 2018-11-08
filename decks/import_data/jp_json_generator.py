# coding: UTF-8
from html.parser import HTMLParser
from bs4 import BeautifulSoup
from collections import Counter
import requests
import re
from copy import copy
import codecs

from abc import ABCMeta, abstractmethod

type_list = ["Grass", "Fire", "Water", "Lightning", "Fighting", "Psychic", "Colorless", "Darkness", "Metal", "Dragon",
             "Fairy", "Free"]
type_tag_list = ["grass", "fire", "water", "electric", "fighting", "psychic", "none", "dark", "steel", "dragon",
                 "fairy", "void"]


def rarity_icon(soup: BeautifulSoup):
    _result = {}
    try:
        rarity_img_url = BeautifulSoup(str(soup.find("div", class_="subtext Text-fjalla")), "lxml").find_all("img")[-1].get("src")
        if "ic_rare_u_c.gif" in rarity_img_url or "ic_rare_u.gif" in rarity_img_url:
            _result.update(rarity="Uncommon")
        elif "ic_rare_c_c.gif" in rarity_img_url or "ic_rare_c.gif" in rarity_img_url:
            _result.update(rarity="Common")
        elif "ic_prismstar.gif" in rarity_img_url:
            _result.update(rarity="Prism Star")
        elif "ic_rare_r_c.gif" in rarity_img_url or "ic_rare_r.gif" in rarity_img_url:
            _result.update(rarity="Rare")
        elif "ic_rare_c2.gif" in rarity_img_url:
            _result.update(rarity="Common Holo")
        elif "ic_rare_u2.gif" in rarity_img_url:
            _result.update(rarity="Uncommon Holo")
        elif "ic_rare_rr.gif" in rarity_img_url:
            _result.update(rarity="RR")
        elif "ic_rare_ur_c.gif" in rarity_img_url:
            _result.update(rarity="UR")
        elif "ic_rare_sr_c.gif" in rarity_img_url:
            _result.update(rarity="SR")
        elif "ic_rare_s.gif" in rarity_img_url:
            _result.update(rarity="Rare Secret")
        elif "ic_rare_ss.gif" in rarity_img_url:
            _result.update(rarity="LEGEND")
        elif "ic_hikaru.gif" in rarity_img_url:
            _result.update(rarity="Shining")
        elif "regulation_logo_1/XYP.gif" in rarity_img_url:
            _result.update(rarity="XY Promo")
        elif "regulation_logo_1/BWP.gif" in rarity_img_url:
            _result.update(rarity="BW Promo")
        elif "regulation_logo_1/DPP.gif" in rarity_img_url:
            _result.update(rarity="DP Promo")
        else:
            if "/assets/images/card/rarity/" in rarity_img_url:
                raise ValueError("Unknown rarity icon：" + rarity_img_url)
        return _result
    except ValueError:
        try:
            print("No rarity icon.", rarity_img_url)
        except UnboundLocalError:
            pass


class MetaHTMLDownloaderAndSplitter(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, card_id: int):
        pass

    @abstractmethod
    def return_leftbox(self):
        """This method should return the innerHTML of 'div.LeftBox'"""
    @abstractmethod
    def return_rightbox(self):
        """This method should return the innerHTML of 'div.RightBox'"""
    @abstractmethod
    def return_card_name(self):
        """This method should return the innerText of 'h1.Heading1'"""
    @abstractmethod
    def return_card_global_id_number(self):
        """This method should return the global_id_number in int'"""


class DownloadAndSplitHTML(MetaHTMLDownloaderAndSplitter):
    def __init__(self, card_id: int):
        self.url = "https://www.pokemon-card.com/card-search/details.php/card/" + str(card_id) + "/regu/all"
        self.soup = BeautifulSoup(requests.get(self.url).content, "lxml")
        self.card_id = card_id

    def return_leftbox(self):
        leftbox_str = str(self.soup.find("div", class_="LeftBox"))
        return leftbox_str

    def return_rightbox(self):
        rightbox_str = str(self.soup.find("div", class_="RightBox"))
        return rightbox_str

    def return_card_name(self):
        if BeautifulSoup(str(self.soup.find("h1", class_="Heading1")), "lxml").find("span", class_="pcg-prismstar"):
            return self.soup.find("h1", class_="Heading1").text + "\u25c7"
        else:
            return self.soup.find("h1", class_="Heading1").text

    def return_card_global_id_number(self):
        return self.card_id


class MetaSpanTagsHTMLStrToTypeStrList(HTMLParser, metaclass=ABCMeta):
    @abstractmethod
    def error(self, message):
        pass

    @abstractmethod
    def handle_starttag(self, tag, attrs):
        """Implement the span class attribute name to type name converter."""

    @abstractmethod
    def get_type_list(self):
        """returns the converted list of type"""


class SpanTagsHTMLStrToTypeStrList(MetaSpanTagsHTMLStrToTypeStrList, HTMLParser):
    def error(self, message):
        pass

    def __init__(self):
        super().__init__()
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


class GetMoveAndAbilityAndRuleInfoFromTag:
    def __init__(self, html_downloader_and_splitter: MetaHTMLDownloaderAndSplitter, move_cost_list_getter: MetaSpanTagsHTMLStrToTypeStrList, ):
        """MetaHTMLDownloaderAndSplitter and MetaSpanTagsHTMLStrToTypeStrList should be an instance."""
        self.move_name = ""
        self.move_cost_list_getter = move_cost_list_getter
        self.html_downloader_and_splitter = html_downloader_and_splitter
        self.move_cost_list = []
        self.soup = None
        self.h4soup = None
        self.move_html_h4_tag_list = []
        self.attack = {}
        self.attacks = []
        self.abilities = []
        self.ability = {}
        self.rule_text = []
        self.info_dict = {}

    def process(self):
        right_box_inner_html_str = self.html_downloader_and_splitter.return_rightbox()
        self.soup = BeautifulSoup(right_box_inner_html_str, "lxml")
        # Start Move part
        move_tags_start_tag = self.soup.find("h2", class_="mt20", text="ワザ")
        if not move_tags_start_tag:
            self.attacks = None
        else:
            move_tags_start_index = self.soup.find_all().index(move_tags_start_tag)
            move_soup = BeautifulSoup(str(self.soup.find_all()[move_tags_start_index:]), "lxml")
            self.move_html_h4_tag_list = move_soup.find_all("h4")
            move_tags_h4_index_number_list = [move_soup.find_all().index(elm) for elm in self.move_html_h4_tag_list]
            move_tags_str_list = []
            for i in range(len(move_tags_h4_index_number_list)):
                if i == (len(move_tags_h4_index_number_list) - 1):
                    move_tags_str_list.append(str(move_soup.find_all()[move_tags_h4_index_number_list[i]:]))
                else:
                    move_tags_str_list.append(str(move_soup.find_all()[
                                              move_tags_h4_index_number_list[i]:move_tags_h4_index_number_list[i+1]]))

            for html_str in move_tags_str_list:
                self.move_cost_list_getter.__init__()
                h4_tag = BeautifulSoup(html_str, "lxml").find("h4")
                self.move_cost_list_getter.feed(str(h4_tag))
                self.move_cost_list = self.move_cost_list_getter.get_type_list()
                self.attack.update(cost=self.move_cost_list)

                h4_tag_copy = copy(h4_tag)
                h4_tag_copy_soup = BeautifulSoup(str(h4_tag_copy), "lxml")
                [s.extract() for s in h4_tag_copy_soup('span')]

                attack_name = re.sub("\s?(\xa0)?\n$", "", h4_tag_copy_soup.text)

                self.attack.update(name=attack_name)
                self.attack.update(damage="".join([
                    elm1.text for elm1 in BeautifulSoup(str(h4_tag), "lxml").find_all("span")]))

                self.attack.update(text=BeautifulSoup(re.sub(
                    r'<span class="icon-([a-z]+) icon"></span>', lambda m: "[[" + type_list[
                        type_tag_list.index(m.group(1))] + "]]", copy(html_str)), "lxml").find_all("p")[1].text)

                self.attack.update(convertedEnergyCost=len(self.move_cost_list) - Counter(self.move_cost_list)["Free"])

                self.attacks.append(self.attack.copy())

        self.info_dict.update(attacks=self.attacks)
        # End move part

        # start ability part
        ability_tags_start_tag = self.soup.find(
            "h2", class_="mt20", text="特性") or self.soup.find(
            "h2", class_="mt20", text="ポケパワー") or self.soup.find(
            "h2", class_="mt20", text="ポケボディー") or self.soup.find(
            "h2", class_="mt20", text="古代能力") or self.soup.find(
            "h2", class_="mt20", text="きのみ") or self.soup.find(
            "h2", class_="mt20", text="どうぐ")
        while ability_tags_start_tag:
            next_start_tag = BeautifulSoup(str(self.soup.find_all()[self.soup.find_all()
                                               .index(ability_tags_start_tag) + 1:]), "lxml").find("h2", class_="mt20")
            soup_reverse = copy(self.soup.find_all())
            soup_reverse.reverse()
            ability_tags = self.soup.find_all()[self.soup.find_all().index(
                ability_tags_start_tag):len(self.soup.find_all()) - soup_reverse.index(next_start_tag) - 1 if next_start_tag else None]
            ability_soup = BeautifulSoup(
                re.sub(r'<span class="icon-([a-z]+) icon"></span>',
                       lambda m: "[[" + type_list[type_tag_list.index(m.group(1))] + "]]", str(ability_tags)), "lxml")

            self.ability.update(name=ability_soup.find("h4").text)
            self.ability.update(text=ability_soup.find_all("p")[1].text)
            if ability_tags_start_tag.text == "特性":
                self.ability.update(type="Ability")
            elif ability_tags_start_tag.text == "ポケパワー":
                self.ability.update(type="Poké-Power")
            elif ability_tags_start_tag.text == "ポケボディー":
                self.ability.update(type="Poké-Body")
            elif ability_tags_start_tag.text == "古代能力":
                self.ability.update(type="Ancient-Trait")
            elif ability_tags_start_tag.text == "きのみ":
                self.ability.update(type="Berry")
            elif ability_tags_start_tag.text == "どうぐ":
                self.ability.update(type="Pok\u00e9mon-Tool")

            self.abilities.append(copy(self.ability))

            if next_start_tag:
                self.soup = BeautifulSoup(str(self.soup.find_all()[len(self.soup.find_all()) - soup_reverse.index(next_start_tag) - 1:]), "lxml")
                ability_tags_start_tag = self.soup.find(
                    "h2", class_="mt20", text="特性") or self.soup.find(
                    "h2", class_="mt20", text="ポケパワー") or self.soup.find(
                    "h2", class_="mt20", text="ポケボディー") or self.soup.find(
                    "h2", class_="mt20", text="古代能力") or self.soup.find(
                    "h2", class_="mt20", text="きのみ") or self.soup.find(
                    "h2", class_="mt20", text="どうぐ")
            else:
                break

        self.info_dict.update(abilities=self.abilities)
        # end ability part

        # start rule(text) part
        text_tags_start_tag = self.soup.find("h2", class_="mt20", text="特別なルール")
        if not text_tags_start_tag:
            self.rule_text = None
        else:
            self.rule_text.append(self.soup.find_all()[self.soup.find_all().index(text_tags_start_tag)+1].text)
            self.info_dict.update(text=self.rule_text)
        # end rule(text) part

        return self.info_dict


class GetWeaknessAndResistanceAndRetreatCost:
    def __init__(self, html_downloader_and_splitter: MetaHTMLDownloaderAndSplitter, move_cost_list_getter: MetaSpanTagsHTMLStrToTypeStrList, ):
        """MetaHTMLDownloaderAndSplitter and MetaSpanTagsHTMLStrToTypeStrList should be an instance."""
        self.move_cost_list_getter = move_cost_list_getter
        self.html_downloader_and_splitter = html_downloader_and_splitter
        self.weaknesses = []
        self.resistances = []
        self.table_soup = None
        self.move_html_td_tag_list = None
        self.move_html_td_str_list = None
        self.retreat_cost = []
        self.attack = {}
        self.attacks = []
        self._result = {}

    def process(self):
        rightbox_html_str = self.html_downloader_and_splitter.return_rightbox()
        self.table_soup = BeautifulSoup(rightbox_html_str, "lxml")
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
        self._result.update(convertedRetreatCost=len(self.retreat_cost))

        return self._result

    def get_value(self):
        # print(self._result)
        return self._result


class GetEvolutionAndSubType:
    def __init__(self, html_downloader_and_splitter: MetaHTMLDownloaderAndSplitter, move_cost_list_getter: MetaSpanTagsHTMLStrToTypeStrList, ):
        """MetaHTMLDownloaderAndSplitter and MetaSpanTagsHTMLStrToTypeStrList should be an instance."""
        self.move_cost_list_getter = move_cost_list_getter
        self.html_downloader_and_splitter = html_downloader_and_splitter
        self.parent = ""
        self.grand_parent = ""
        self.great_grand_parent = ""
        self.children_list = []
        self.grand_children_list = []
        self.great_grand_children_list = []

        self.evolutiou_type_text = ""

        self.soup = None
        self.evolution_list_list = None
        self.pokemon_name = None

    def process(self):
        rightbox_html_str = self.html_downloader_and_splitter.return_rightbox()
        self.soup = BeautifulSoup(rightbox_html_str, "lxml")

        if self.soup.find_all("span", class_="type"):
            self.evolutiou_type_text = self.soup.find("span", class_="type").text

        if self.soup.find_all("div", class_="evolution"):
            evolution_tags_list = self.soup.find_all("div", class_="evolution")
            self.evolution_list_list = [[a_tag.text.replace("\n", "") for a_tag in BeautifulSoup(str(tag), "lxml")
                .find_all(class_=re.compile("ev_.*"))] for tag in evolution_tags_list]
            # reverse to make the list basic first
            self.evolution_list_list.reverse()
            self.pokemon_name = self.html_downloader_and_splitter.return_card_name()
        # if the pokmon does not evolve
        if not self.pokemon_name:
            return {"evolution_list_list": None,
                    "evolvesFrom": None,
                    "subtype": "Basic", }
        # # if the pokemon is basic
        # if not self.pokemon_name:
        #     return {"evolution_list_list": self.evolution_list_list, "evolvesFrom": None}

        for i in range(len(self.evolution_list_list)):
            try:
                pos = (i, self.evolution_list_list[i].index(self.pokemon_name))
                break
            except ValueError:
                try:
                    name_original = self.pokemon_name.replace("[Exeggutor]", "").replace("ex", "")
                    pos = (i, self.evolution_list_list[i].index(name_original))
                except ValueError:
                    try:
                        if "M[ムービー]" in self.pokemon_name or "G[ギンガ]" in self.pokemon_name:
                            f = codecs.open(r"out1_dir/data/error.log", "a", "utf-8")
                            f.write(self.pokemon_name)
                            f.close()
                            return {"evolution_list_list": [[self.pokemon_name]],
                                    "evolvesFrom": None,
                                    "subtype": "Basic"}

                    except ValueError:
                        raise ValueError
        try:
            if self.evolutiou_type_text == "たね":
                return {"evolution_list_list": self.evolution_list_list,
                        "evolvesFrom": None,
                        "subtype": "Basic"}

            else:
                for i in range(pos[1] + 1):
                    try:
                        def throw_error():
                            raise ValueError("Global id =", self.html_downloader_and_splitter.return_card_global_id_number())

                        return {"evolution_list_list": self.evolution_list_list,
                                "evolvesFrom": self.evolution_list_list[pos[0]-1][pos[1] - i],
                                "subtype": ("Basic" if self.evolutiou_type_text == "たね"
                                            else "BREAK" if re.match(".*BREAK$", self.pokemon_name)
                                            else "Stage 1" if re.match("1\s進化", self.evolutiou_type_text)
                                            else "Srage 2" if re.match("2\s進化", self.evolutiou_type_text)
                                            else "Level Up" if self.evolutiou_type_text == "レベルアップ"
                                            else "MEGA" if self.evolutiou_type_text == "M進化"
                                            else "Restored" if self.evolutiou_type_text == "復元"
                                            else throw_error())}
                    except IndexError:
                            pass
        except UnboundLocalError:
            import traceback
            if self.pokemon_name == "ずがいの化石":
                return {"evolution_list_list": [["ずがいの化石"], ["ズガイドス"], ["ラムパルド"]],
                        "evolvesFrom": None,
                        "subtype": "Basic"}
            elif self.pokemon_name == "ズガイドス":
                return {"evolution_list_list": [["ずがいの化石"], ["ズガイドス"], ["ラムパルド"]],
                        "evolvesFrom": "ずがいの化石",
                        "subtype": "Stage 1"}
            elif self.pokemon_name == "ラムパルド":
                return {"evolution_list_list": [["ずがいの化石"], ["ズガイドス"], ["ラムパルド"]],
                        "evolvesFrom": "ズガイドス",
                        "subtype": "Stage 2"}
            else:
                traceback.print_exc()

    def get_evolution_info(self):
        return self.process()



class GetPokemonAllInfo:
    def __init__(self, global_id_number):
        self.html_downloader_and_splitter = DownloadAndSplitHTML(global_id_number)
        self.move_cost_list_getter = SpanTagsHTMLStrToTypeStrList()

        self.card_id_and_image_url_and_artist_getter = GetCardNameAndIDAndImageURLAndArtist(
            self.html_downloader_and_splitter, self.move_cost_list_getter)
        self.pokemon_basic_info_getter = GetPokemonBasicInfo(
            self.html_downloader_and_splitter, self.move_cost_list_getter)
        self.move_and_ability_and_rule_info_from_tag_getter = GetMoveAndAbilityAndRuleInfoFromTag(
            self.html_downloader_and_splitter, self.move_cost_list_getter)
        self.weakness_and_resistance_and_retreat_cost_getter = GetWeaknessAndResistanceAndRetreatCost(
            self.html_downloader_and_splitter, self.move_cost_list_getter)
        self.evolution_and_sub_type_getter = GetEvolutionAndSubType(
            self.html_downloader_and_splitter, self.move_cost_list_getter)

        self._result_dict = {"supertype": "Pok\u00e9mon"}

    def get_info(self):

        self._result_dict.update(self.card_id_and_image_url_and_artist_getter.process())
        self._result_dict.update(self.pokemon_basic_info_getter.process())
        self._result_dict.update(self.move_and_ability_and_rule_info_from_tag_getter.process())
        self._result_dict.update(self.weakness_and_resistance_and_retreat_cost_getter.process())
        self._result_dict.update(self.evolution_and_sub_type_getter.process())
        return self._result_dict


# class GetPokemonAllInfo:
#     def __init__(self, html_downloader_and_splitter: MetaHTMLDownloaderAndSplitter, move_cost_list_getter: MetaSpanTagsHTMLStrToTypeStrList, card_id_and_image_url_and_artist_getter, pokemon_basic_info_getter, move_and_ability_and_rule_info_from_tag_getter, weakness_and_resistance_and_retreat_cost_getter, evolution_and_sub_type_getter):
#         """all classes from arguments must be instances."""
#         self.move_cost_list_getter = move_cost_list_getter
#         self.html_downloader_and_splitter = html_downloader_and_splitter
#
#         self.card_id_and_image_url_and_artist_getter = card_id_and_image_url_and_artist_getter
#         self.pokemon_basic_info_getter = pokemon_basic_info_getter
#         self.move_and_ability_and_rule_info_from_tag_getter = move_and_ability_and_rule_info_from_tag_getter
#         self.weakness_and_resistance_and_retreat_cost_getter = weakness_and_resistance_and_retreat_cost_getter
#         self.evolution_and_sub_type_getter = evolution_and_sub_type_getter
#
#         self._result_dict = {}
#
#     def get_dict_data(self, global_id_number: int):
#         self._result_dict.update(self.card_id_and_image_url_and_artist_getter.__init__(self.html_downloader_and_splitter.__init__(global_id_number), self.move_cost_list_getter))
#         self._result_dict.update(self.pokemon_basic_info_getter.__init__(self.html_downloader_and_splitter.__init__(global_id_number), self.move_cost_list_getter))
#         self._result_dict.update(self.move_and_ability_and_rule_info_from_tag_getter.__init__(self.html_downloader_and_splitter.__init__(global_id_number), self.move_cost_list_getter))
#         self._result_dict.update(self.weakness_and_resistance_and_retreat_cost_getter.__init__(self.html_downloader_and_splitter.__init__(global_id_number), self.move_cost_list_getter))
#         self._result_dict.update(self.evolution_and_sub_type_getter.__init__(self.html_downloader_and_splitter.__init__(global_id_number), self.move_cost_list_getter))


class GetPokemonBasicInfo:
    def __init__(self, html_downloader_and_splitter: MetaHTMLDownloaderAndSplitter, move_cost_list_getter: MetaSpanTagsHTMLStrToTypeStrList, ):
        """MetaHTMLDownloaderAndSplitter and MetaSpanTagsHTMLStrToTypeStrList should be an instance."""
        self.move_cost_list_getter = move_cost_list_getter
        self.html_downloader_and_splitter = html_downloader_and_splitter
        self.types = []
        self.hp = "0"
        self._result = {}

    def process(self):
        rightbox_html_str = self.html_downloader_and_splitter.return_rightbox()
        top_info_soup = BeautifulSoup(str(BeautifulSoup(rightbox_html_str, "lxml")
                                          .find("div", class_="TopInfo Text-fjalla")), "lxml")
        self.hp = top_info_soup.find("span", class_="hp-num").text
        self.move_cost_list_getter.feed(str(top_info_soup.find("div", class_="td-r")))
        self.types = self.move_cost_list_getter.get_type_list()
        level_tag = top_info_soup.find("span", class_="level-num")
        if level_tag:
            return {"hp": self.hp, "types": self.types, "level": level_tag.text}
        else:
            return {"hp": self.hp, "types": self.types}


class GetCardNameAndIDAndImageURLAndArtist:
    def __init__(self, html_downloader_and_splitter: MetaHTMLDownloaderAndSplitter, move_cost_list_getter: MetaSpanTagsHTMLStrToTypeStrList, ):
        """MetaHTMLDownloaderAndSplitter and MetaSpanTagsHTMLStrToTypeStrList should be an instance."""
        self.move_cost_list_getter = move_cost_list_getter
        self.html_downloader_and_splitter = html_downloader_and_splitter
        self._result = {}
        self.image_url = ""
        self.id = ""
        self.global_id_number = -1
        self.artist = ""
        self.setCode = ""
        self.card_name = self.html_downloader_and_splitter.return_card_name()
        self.soup = None

    def process(self):
        self._result.update(name=self.card_name)
        leftbox_html_str = self.html_downloader_and_splitter.return_leftbox()
        self.soup = BeautifulSoup(leftbox_html_str, "lxml")

        if self.soup.find("img", class_="img-regulation"):
            self.setCode = self.soup.find("img", class_="img-regulation").get("alt")
            self._result.update(setCode=self.setCode)

        set_text = self.soup.find("div", class_="subtext Text-fjalla").text
        if re.search("^[a-zA-Z]+-P$", set_text.replace(" ", "").replace("\xa0", "").replace("\n", "").replace("\t", "")):
            self._result.update(id=set_text.replace(" ", "").replace("\xa0", "").replace("\n", "").replace("\t", ""))

        elif "(上)" in set_text and "(下)" in set_text:
            set_text = set_text.replace(" ", "").replace("\xa0", "").replace("\n", "").replace("\t", "")
            search_result = re.search("([0-9]+)/([0-9]+)\(上\)([0-9]+)/([0-9]+)", set_text)
            self.id = self.setCode + "-" + search_result.group(1) + "," + self.setCode + "-" + search_result.group(3)
            self._result.update(id=self.id)
        elif set_text.replace(" ", "").replace("\xa0", "").replace("\n", "").replace("\t", ""):
            set_text = set_text.replace(" ", "").replace("\xa0", "").replace("\n", "").replace("\t", "")
            if re.search("^DPBP#[0-9]+$", set_text):
                self.id = self.setCode + "-" + set_text
                self._result.update(id=self.id)
            else:
                self.id = self.setCode + "-" + str(int(re.sub("/([0-9]+)?([a-zA-Z]+(-P)?)?(DPBP#[0-9]+)?$", "", self.soup.find("div", class_="subtext Text-fjalla").text.replace(" ", "").replace("\xa0", "").replace("\n", "").replace("\t", "").replace("XY-P", ""))))
                self._result.update(id=self.id)
        else:
            pass

        rarity_icon_dict = rarity_icon(self.soup)
        if rarity_icon_dict:
            self._result.update(rarity_icon(self.soup))

        if BeautifulSoup(str(self.soup.find("div", class_="author")), "lxml").find("a"):
            self.artist = BeautifulSoup(str(self.soup.find("div", class_="author")), "lxml").find("a").text
            self._result.update(artist=self.artist)

        self.image_url = "https://www.pokemon-card.com" + self.soup.find("img", class_="fit").get("src")
        self._result.update(imageUrl=self.image_url, imageUrlHiRes=self.image_url)

        self.global_id_number = self.html_downloader_and_splitter.return_card_global_id_number()
        self._result.update(global_id_number=self.global_id_number)

        return self._result

    def get_result(self):
        # return {"id": self.id, "setCode": self.setCode, "global_id_number": self.global_id_number,
        #         "artist": self.artist, "imageUrl": self.image_url, "imageUrlHiRes": self.image_url}
        return self._result


class DetectCardType:
    def __init__(self, html_downloader_and_splitter: MetaHTMLDownloaderAndSplitter):
        self.html_downloader_and_splitter = html_downloader_and_splitter
        self.soup = BeautifulSoup(self.html_downloader_and_splitter.return_rightbox(), "lxml")

    def get_type_dict(self):
        h2_mt20_text = self.soup.find("h2", class_="mt20").string
        if h2_mt20_text == "ワザ" or h2_mt20_text == "古代能力" or h2_mt20_text == "特性" or h2_mt20_text ==\
                "ポケパワー" or h2_mt20_text == "ポケボディー" or h2_mt20_text == "きのみ" or h2_mt20_text == "どうぐ":
            return {"supertype": "Pok\u00e9mon", }
        elif h2_mt20_text == "サポート":
            return {"supertype": "Trainer", "subtype": "Supporter", }
        elif h2_mt20_text == "グッズ":
            return {"supertype": "Trainer", "subtype": "Item", }
        elif h2_mt20_text == "トレーナー":
            return {"supertype": "Trainer", "subtype": "Item-fossil", }
        elif h2_mt20_text == "ポケモンのどうぐ":
            return  {"supertype": "Trainer", "subtype": "Pok\u00e9mon Tool", }
        elif h2_mt20_text == "スタジアム":
            return  {"supertype": "Trainer", "subtype": "Stadium", }
        elif h2_mt20_text == "特殊エネルギー":
            return  {"supertype": "Energy", "subtype": "Special", }
        elif h2_mt20_text == "基本エネルギー":
            return  {"supertype": "Energy", "subtype": "Basic", }
        elif h2_mt20_text == "ワザマシン":
            return {"supertype": "Trainer", "subtype": "Technical Machine", }
        else:
            raise(ValueError(
                "Unknown super type: " + h2_mt20_text + self.html_downloader_and_splitter.return_card_name()))


class GetEnergyAllInfo:
    def __init__(self, global_id_number: int, sub_type: str):
        self.global_id_number = global_id_number
        self.subtype = sub_type

        self.html_downloader_and_splitter = DownloadAndSplitHTML(self.global_id_number)

        self.card_name = self.html_downloader_and_splitter.return_card_name()
        self.left_box_soup = None
        self.right_box_soup = None
        self.setCode = None
        self._result = {"supertype": "Energy", "subtype": self.subtype}
        self.rule_text = []

    def get_info(self):
        self._result.update(name=self.card_name)
        leftbox_html_str = self.html_downloader_and_splitter.return_leftbox()
        self.left_box_soup = BeautifulSoup(leftbox_html_str, "lxml")

        if self.left_box_soup.find("img", class_="img-regulation"):
            self.setCode = self.left_box_soup.find("img", class_="img-regulation").get("alt")
            self._result.update(setCode=self.setCode)

        set_text = self.left_box_soup.find("div", class_="subtext Text-fjalla").text
        if not ("/" in set_text):
            self._result.update(id=self.setCode)
        elif set_text.replace(" ", "").replace("\xa0", "").replace("\n", ""):
            self.id = self.setCode + "-" + str(int(re.sub("/([0-9]+)?([a-zA-Z]+(-P)?)?(DPBP#[0-9]+)?$", "", self.left_box_soup.find("div",
                                                                                                  class_="subtext Text-fjalla").text.replace(
                " ", "").replace("\xa0", "").replace("\n", ""))))
            self._result.update(id=self.id)
        else:
            pass

        rarity_icon_dict = rarity_icon(self.left_box_soup)
        if rarity_icon_dict:
            self._result.update(rarity_icon(self.left_box_soup))

        if BeautifulSoup(str(self.left_box_soup.find("div", class_="author")), "lxml").find("a"):
            self.artist = BeautifulSoup(str(self.left_box_soup.find("div", class_="author")), "lxml").find("a").text
            self._result.update(artist=self.artist)

        self.image_url = "https://www.pokemon-card.com" + self.left_box_soup.find("img", class_="fit").get("src")
        self._result.update(imageUrl=self.image_url, imageUrlHiRes=self.image_url)

        self.global_id_number = int(self.image_url.split("/")[-1].split("_")[0])
        self._result.update(global_id_number=self.global_id_number)

        # end_left_box part

        # start right_box part

        rightbox_html_str = self.html_downloader_and_splitter.return_rightbox()
        self.right_box_soup = BeautifulSoup(rightbox_html_str, "lxml")
        # start text part
        text_tags_start_tag = self.right_box_soup.find("h2", class_="mt20", text="特殊エネルギー")
        if not text_tags_start_tag:
            pass
        else:
            next_start_tag = BeautifulSoup(str(self.right_box_soup.find_all()[self.right_box_soup.find_all()
                                               .index(text_tags_start_tag) + 1:]), "lxml").find("h2", class_="mt20")
            if next_start_tag:
                text_tags = self.right_box_soup.find_all()[self.right_box_soup.find_all().index(
                    text_tags_start_tag):self.right_box_soup.find_all().index(next_start_tag)]
            else:
                text_tags = self.right_box_soup.find_all()[self.right_box_soup.find_all().index(
                    text_tags_start_tag):]

            text_soup = BeautifulSoup(re.sub(r'<span class="icon-([a-z]+) icon"></span>',
                                                lambda m: "[[" + type_list[type_tag_list.index(m.group(1))] + "]]",
                                                str(text_tags)), "lxml")
            try:
                self.rule_text.append(text_soup.find_all("p")[1].text)
            except IndexError:
                pass


            self._result.update(text=self.rule_text)
        # end text part

        # start rule(text) part
        text_tags_start_tag = self.right_box_soup.find("h2", class_="mt20", text="特別なルール")
        if not text_tags_start_tag:
            pass
        else:
            next_start_tag = BeautifulSoup(str(self.right_box_soup.find_all()[self.right_box_soup.find_all()
                                               .index(text_tags_start_tag) + 1:]), "lxml").find("h2", class_="mt20")
            if next_start_tag:
                text_tags = self.right_box_soup.find_all()[self.right_box_soup.find_all().index(
                    text_tags_start_tag):self.right_box_soup.find_all().index(next_start_tag)]
            else:
                text_tags = self.right_box_soup.find_all()[self.right_box_soup.find_all().index(
                    text_tags_start_tag):]

            text_soup = BeautifulSoup(re.sub(r'<span class="icon-([a-z]+) icon"></span>',
                                                lambda m: "[[" + type_list[type_tag_list.index(m.group(1))] + "]]",
                                                str(text_tags)), "lxml")
            try:
                self.rule_text.append(text_soup.find_all("p")[1].text)
            except IndexError:
                pass

            self._result.update(text=self.rule_text)
        # end rule(text) part

        return self._result


class GetTrainersAllInfo:
    def __init__(self, global_id_number: int, sub_type: str):
        self.global_id_number = global_id_number
        self.subtype = sub_type

        self.html_downloader_and_splitter = DownloadAndSplitHTML(self.global_id_number)

        self.card_name = self.html_downloader_and_splitter.return_card_name()
        self.left_box_soup = None
        self.right_box_soup = None
        self._result = {"supertype": "Trainer", "subtype": self.subtype}
        self.rule_text = []

    def get_info(self):
        self._result.update(name=self.card_name)
        leftbox_html_str = self.html_downloader_and_splitter.return_leftbox()
        self.left_box_soup = BeautifulSoup(leftbox_html_str, "lxml")

        if self.left_box_soup.find("img", class_="img-regulation"):
            self.setCode = self.left_box_soup.find("img", class_="img-regulation").get("alt")
            self._result.update(setCode=self.setCode)

        set_text = self.left_box_soup.find("div", class_="subtext Text-fjalla").text

        if re.search("^[a-zA-Z]+-P$", set_text.replace(" ", "").replace("\xa0", "").replace("\n", "").replace("\t", "")):
            self._result.update(id=set_text.replace(" ", "").replace("\xa0", "").replace("\n", "").replace("\t", ""))

        elif set_text.replace(" ", "").replace("\xa0", "").replace("\n", "") and re.sub("/([0-9]+)?([a-zA-Z]+(-P」?)?)?(DPBP#[0-9]+)?$", "", self.left_box_soup.find("div",
                                                                                                  class_="subtext Text-fjalla").text.replace(
                " ", "").replace("\xa0", "").replace("\n", "")) != "－":
            self.id = self.setCode + "-" + str(int(re.sub("/([0-9]+)?([a-zA-Z]+(-P」?)?)?(DPBP#[0-9]+)?$", "", self.left_box_soup.find("div",
                                                                                                  class_="subtext Text-fjalla").text.replace(
                " ", "").replace("\xa0", "").replace("\n", ""))))
            self._result.update(id=self.id)
        else:
            pass

        rarity_icon_dict = rarity_icon(self.left_box_soup)
        if rarity_icon_dict:
            self._result.update(rarity_icon(self.left_box_soup))

        if BeautifulSoup(str(self.left_box_soup.find("div", class_="author")), "lxml").find("a"):
            self.artist = BeautifulSoup(str(self.left_box_soup.find("div", class_="author")), "lxml").find("a").text
            self._result.update(artist=self.artist)

        self.image_url = "https://www.pokemon-card.com" + self.left_box_soup.find("img", class_="fit").get("src")
        self._result.update(imageUrl=self.image_url, imageUrlHiRes=self.image_url)

        self.global_id_number = self.html_downloader_and_splitter.return_card_global_id_number()
        self._result.update(global_id_number=self.global_id_number)

        # end_left_box part

        # start right_box part

        rightbox_html_str = self.html_downloader_and_splitter.return_rightbox()
        self.right_box_soup = BeautifulSoup(rightbox_html_str, "lxml")
        # start text part
        text_tags_start_tag = self.right_box_soup.find("h2", class_="mt20", text="スタジアム") or self.right_box_soup.find("h2", class_="mt20", text="グッズ") or self.right_box_soup.find("h2", class_="mt20", text="ポケモンのどうぐ") or self.right_box_soup.find("h2", class_="mt20", text="サポート")
        if not text_tags_start_tag:
            pass
        else:
            next_start_tag = BeautifulSoup(str(self.right_box_soup.find_all()[self.right_box_soup.find_all()
                                               .index(text_tags_start_tag) + 1:]), "lxml").find("h2", class_="mt20")
            if next_start_tag:
                text_tags = self.right_box_soup.find_all()[self.right_box_soup.find_all().index(
                    text_tags_start_tag):self.right_box_soup.find_all().index(next_start_tag)]
            else:
                text_tags = self.right_box_soup.find_all()[self.right_box_soup.find_all().index(
                    text_tags_start_tag):]

            text_soup = BeautifulSoup(re.sub(r'<span class="icon-([a-z]+) icon"></span>',
                                             lambda m: "[[" + type_list[type_tag_list.index(m.group(1))] + "]]",
                                             str(text_tags)), "lxml")
            try:
                self.rule_text.append(text_soup.find_all("p")[1].text)
            except IndexError:
                pass

            self._result.update(text=self.rule_text)
        # end text part

        # start rule(text) part
        text_tags_start_tag = self.right_box_soup.find("h2", class_="mt20", text="特別なルール")
        if not text_tags_start_tag:
            pass
        else:
            next_start_tag = BeautifulSoup(str(self.right_box_soup.find_all()[self.right_box_soup.find_all()
                                               .index(text_tags_start_tag) + 1:]), "lxml").find("h2", class_="mt20")
            if next_start_tag:
                text_tags = self.right_box_soup.find_all()[self.right_box_soup.find_all().index(
                    text_tags_start_tag):self.right_box_soup.find_all().index(next_start_tag)]
            else:
                text_tags = self.right_box_soup.find_all()[self.right_box_soup.find_all().index(
                    text_tags_start_tag):]

            text_soup = BeautifulSoup(re.sub(r'<span class="icon-([a-z]+) icon"></span>',
                                             lambda m: "[[" + type_list[type_tag_list.index(m.group(1))] + "]]",
                                             str(text_tags)), "lxml")
            try:
                self.rule_text.append(text_soup.find_all("p")[1].text)
            except IndexError:
                pass

            self._result.update(text=self.rule_text)
        # end rule(text) part

        return self._result


class GetCardInfo:
    def __init__(self, global_id_number: int):
        self.global_id_number = global_id_number

        self.html_downloader_and_splitter = DownloadAndSplitHTML(global_id_number)
        self.move_cost_list_getter = SpanTagsHTMLStrToTypeStrList()

        self.detect_card_type = DetectCardType(self.html_downloader_and_splitter)

    def get_info(self):
        dict_data = self.detect_card_type.get_type_dict()
        if dict_data["supertype"] == "Pok\u00e9mon":
            return GetPokemonAllInfo(self.global_id_number).get_info()
        elif dict_data["supertype"] == "Energy":
            return GetEnergyAllInfo(self.global_id_number, dict_data["subtype"]).get_info()
        elif dict_data["supertype"] == "Trainer":
            return GetTrainersAllInfo(self.global_id_number, dict_data["subtype"]).get_info()




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
    # move_cost_list_getter_1 = SpanTagsHTMLStrToTypeStrList()
    # test = GetWeaknessAndResistanceAndRetreatCost(move_cost_list_getter_1)
    # test.feed(
    #     r' <div class="TopInfo Text-fjalla"> <div class="tr"> <div class="td-l"> <span class="type">2&nbsp;進化</span> </div> <div class="td-r"> <span class="hp">HP</span> <span class="hp-num">240</span> <span class="hp-type">タイプ</span> <span class="icon-grass icon"></span> </div> </div> </div><h2 class="mt20">ワザ</h2><h4><span class="icon-grass icon"></span>まどわす <span class="f_right Text-fjalla">40</span></h4><p>相手のバトルポケモンをこんらんにする。</p><h4><span class="icon-grass icon"></span><span class="icon-none icon"></span><span class="icon-none icon"></span>じんつうりき <span class="f_right Text-fjalla">90＋</span></h4><p>自分の手札と相手の手札が同じ枚数なら、90ダメージ追加。</p><h2 class="mt20">GXワザ</h2><h4><span class="icon-grass icon"></span><span class="icon-none icon"></span><span class="icon-none icon"></span>ふくまでんGX &nbsp;</h4><p>相手のポケモン1匹と、ついているすべてのカードを、相手の山札にもどして切る。［対戦中、自分はGXワザを1回しか使えない。］</p><h2 class="mt20">特別なルール</h2><p>ポケモンGXがきぜつしたとき、相手はサイドを2枚とる。</p> <table cellspacing="0" cellpadding="0"> <tbody><tr> <th>弱点</th> <th>抵抗力</th> <th>にげる</th> </tr> <tr> <td><span class="icon-fire icon"></span>×2</td> <td>--</td> <td class="escape"><span class="icon-none icon"></span><span class="icon-none icon"></span></td> </tr> </tbody></table> <h2 class="mt20">進化</h2><div class="evolution evbox"><div class="in-box ev_on"><a href="/card-search/index.php?regulation_detail=XY&amp;pokemon=%E3%83%80%E3%83%BC%E3%83%86%E3%83%B3%E3%82%B0GX">ダーテングGX</a></div><div class="in-box ev_off"><a href="/card-search/index.php?regulation_detail=XY&amp;pokemon=%E3%83%80%E3%83%BC%E3%83%86%E3%83%B3%E3%82%B0">ダーテング</a></div></div><div class="evolution ev_off"><a href="/card-search/index.php?regulation_detail=XY&amp;pokemon=%E3%82%B3%E3%83%8E%E3%83%8F%E3%83%8A">コノハナ</a><div class="arrow_off"></div></div><div class="evolution ev_off"><a href="/card-search/index.php?regulation_detail=XY&amp;pokemon=%E3%82%BF%E3%83%8D%E3%83%9C%E3%83%BC">タネボー</a><div class="arrow_off"></div></div> <span class="Text-annotation mt10">「進化」はスタンダードレギュレーションのものです </span> ')
    # test.get_value()

    # # start DownloadAndSplitHTML part
    # test_1 = DownloadAndSplitHTML(33127)
    # print(test_1.return_card_name())
    # print("---")
    # print(test_1.return_leftbox())
    # print("---")
    # print(test_1.return_rightbox())
    # # # end DownloadAndSplitHTML part
    #
    # # start GetEvolutionAndSubType test
    # test_2 = GetEvolutionAndSubType(DownloadAndSplitHTML(3091), SpanTagsHTMLStrToTypeStrList())
    # test_2.process()
    # print(test_2.get_evolution_info())
    # # end GetEvolutionAndSubType test
    #
    # # start DetectSuperType test
    #
    # test_3 = DetectCardType(DownloadAndSplitHTML(33124))
    # print(test_3.get_super_type_str())
    # #
    # # test4 = GetMoveAndAbilityAndRuleInfoFromTag(DownloadAndSplitHTML(3091), SpanTagsHTMLStrToTypeStrList())
    # # print(test4.process())
    # #
    # # test5 = GetWeaknessAndResistanceAndRetreatCost(DownloadAndSplitHTML(3091), SpanTagsHTMLStrToTypeStrList())
    # # print(test5.process())
    # #
    # # test_6 = GetPokemonBasicInfo(DownloadAndSplitHTML(3091), SpanTagsHTMLStrToTypeStrList())
    # # print(test_6.process())
    # #
    # test_7 = GetCardNameAndIDAndImageURLAndArtist(DownloadAndSplitHTML(31997), SpanTagsHTMLStrToTypeStrList())
    # test_7.process()
    # print(test_7.get_result())

    global_id = 15042
    test_pokemon_all = GetCardInfo(global_id)
    print(test_pokemon_all.get_info())






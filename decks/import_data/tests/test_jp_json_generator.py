from unittest import TestCase
from ..jp_json_generator import *


class TestSpanToTypeList1(TestCase):
    def setUp(self):
        self.span_instance_class = SpanTagsHTMLStrToTypeStrList()
        self.span_instance_class.feed(r'<span class="icon-grass icon"></span><span class="icon-electric icon"></span>'
                                      r'<span class="icon-none icon"></span>ドラゴンブレイク'
                                      r' <span class="f_right Text-fjalla">30×</span>')

    def test_handle_starttag(self):
        self.assertEqual(["Grass", "Lightning", "Colorless"], self.span_instance_class.get_type_list())


class TestSpanToTypeList2(TestCase):
    def setUp(self):
        self.span_instance_class = SpanTagsHTMLStrToTypeStrList()
        self.span_instance_class.feed(r'<span class="icon-void icon"></span>トゲのよろい '
                                      r'<span class="f_right Text-fjalla">30</span>')

    def test_handle_starttag(self):
        self.assertEqual(["Free"], self.span_instance_class.get_type_list())


class TestWRRGetter(TestCase):
    def setUp(self):
        self.move_cost_list_getter_2 = SpanTagsHTMLStrToTypeStrList()
        self.test = GetWeaknessAndResistanceAndRetreatCost(self.move_cost_list_getter_2)
        self.test.process(
            r' <div class="TopInfo Text-fjalla"> <div class="tr"> <div class="td-l"> <span class="type">2&nbsp;進化</span> </div> <div class="td-r"> <span class="hp">HP</span> <span class="hp-num">240</span> <span class="hp-type">タイプ</span> <span class="icon-grass icon"></span> </div> </div> </div><h2 class="mt20">ワザ</h2><h4><span class="icon-grass icon"></span>まどわす <span class="f_right Text-fjalla">40</span></h4><p>相手のバトルポケモンをこんらんにする。</p><h4><span class="icon-grass icon"></span><span class="icon-none icon"></span><span class="icon-none icon"></span>じんつうりき <span class="f_right Text-fjalla">90＋</span></h4><p>自分の手札と相手の手札が同じ枚数なら、90ダメージ追加。</p><h2 class="mt20">GXワザ</h2><h4><span class="icon-grass icon"></span><span class="icon-none icon"></span><span class="icon-none icon"></span>ふくまでんGX &nbsp;</h4><p>相手のポケモン1匹と、ついているすべてのカードを、相手の山札にもどして切る。［対戦中、自分はGXワザを1回しか使えない。］</p><h2 class="mt20">特別なルール</h2><p>ポケモンGXがきぜつしたとき、相手はサイドを2枚とる。</p> <table cellspacing="0" cellpadding="0"> <tbody><tr> <th>弱点</th> <th>抵抗力</th> <th>にげる</th> </tr> <tr> <td><span class="icon-fire icon"></span>×2</td> <td>--</td> <td class="escape"><span class="icon-none icon"></span><span class="icon-none icon"></span></td> </tr> </tbody></table> <h2 class="mt20">進化</h2><div class="evolution evbox"><div class="in-box ev_on"><a href="/card-search/index.php?regulation_detail=XY&amp;pokemon=%E3%83%80%E3%83%BC%E3%83%86%E3%83%B3%E3%82%B0GX">ダーテングGX</a></div><div class="in-box ev_off"><a href="/card-search/index.php?regulation_detail=XY&amp;pokemon=%E3%83%80%E3%83%BC%E3%83%86%E3%83%B3%E3%82%B0">ダーテング</a></div></div><div class="evolution ev_off"><a href="/card-search/index.php?regulation_detail=XY&amp;pokemon=%E3%82%B3%E3%83%8E%E3%83%8F%E3%83%8A">コノハナ</a><div class="arrow_off"></div></div><div class="evolution ev_off"><a href="/card-search/index.php?regulation_detail=XY&amp;pokemon=%E3%82%BF%E3%83%8D%E3%83%9C%E3%83%BC">タネボー</a><div class="arrow_off"></div></div> <span class="Text-annotation mt10">「進化」はスタンダードレギュレーションのものです </span> ')

    def test_result(self):
        self.assertEqual(dict({'weaknesses': [{'type': 'Fire', 'value': '×2'}], 'resistances': [], 'retreatCost': ['Colorless', 'Colorless']}), self.test.get_value())


class TestGetMoveAndAbilityAndRuleInfoFromTag(TestCase):
    def setUp(self):
        self.move_cost_list_getter = SpanTagsHTMLStrToTypeStrList()
        self.test = GetMoveAndAbilityAndRuleInfoFromTag(self.move_cost_list_getter)
        self.test.process()



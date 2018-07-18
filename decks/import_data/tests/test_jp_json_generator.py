from ..jp_json_generator import *
from unittest import TestCase

class TestSpanToTypeList1(TestCase):
    def setUp(self):
        self.span_instance_class = SpanTagsHTMLStrToTypeStrList()
        self.span_instance_class.feed(r'<span class="icon-grass icon"></span><span class="icon-electric icon"></span>'
                                      r'<span class="icon-none icon"></span>ドラゴンブレイク'
                                      r' <span class="f_right Text-fjalla">30×</span>')

    def test_handle_starttag(self):
        self.assertEqual(["Grass", "Lightning", "Colorless"], self.span_instance_class.get_result_list())


class TestSpanToTypeList2(TestCase):
    def setUp(self):
        self.span_instance_class = SpanTagsHTMLStrToTypeStrList()
        self.span_instance_class.feed(r'<span class="icon-void icon"></span>トゲのよろい '
                                      r'<span class="f_right Text-fjalla">30</span>')

    def test_handle_starttag(self):
        self.assertEqual(["Free"], self.span_instance_class.get_result_list())




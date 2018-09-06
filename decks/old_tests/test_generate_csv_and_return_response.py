from unittest import TestCase
from ..proxy_maker import generate_csv_and_return_response

class TestGenerate_csv_and_return_response(TestCase):
    def test_generate_csv_and_return_response(self):
        generate_csv_and_return_response("6giLgL-QUBTxa-NQQ6gi")

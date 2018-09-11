import random
from django import template

register = template.Library()

@register.simple_tag
def random_color():
    rgb_color_str = "rgb(" + (str(random.randint(0, 255)) + ",") * 2 + str(random.randint(0, 255)) + ")"
    return rgb_color_str



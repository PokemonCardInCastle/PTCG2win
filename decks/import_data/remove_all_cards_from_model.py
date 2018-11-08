import sys
import os
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "../../")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PTCG2win.settings')
django.setup()

from decks.models import *


cards = Card.objects.all()

for card in cards:
    card.delete()


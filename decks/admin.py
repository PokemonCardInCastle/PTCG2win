from django.contrib import admin

from accounts.models import PTCG2winUser
from .models import Deck, ArchType, Set, Regulation, Region, Card, CardBundle, PokemonRegion, DeckCode, Rarity, Series
# Register your models here.


admin.site.register(CardBundle)
admin.site.register(Deck)
admin.site.register(Card)
admin.site.register(ArchType)
admin.site.register(Set)
admin.site.register(Regulation)
admin.site.register(Region)
admin.site.register(PokemonRegion)
admin.site.register(Rarity)
admin.site.register(Series)




class DeckCodeAdmin(admin.ModelAdmin):
    list_display = ("text", "date", "ip")


admin.site.register(DeckCode, DeckCodeAdmin)

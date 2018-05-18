from django.contrib import admin
from .models import Deck, User, ArchType, Expansion, Regulation, Region
# Register your models here.

admin.site.register(Deck)
admin.site.register(User)
admin.site.register(ArchType)
admin.site.register(Expansion)
admin.site.register(Regulation)
admin.site.register(Region)

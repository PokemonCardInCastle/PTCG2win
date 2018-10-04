from django.db import models
from accounts.models import PTCG2winUser


class Region(models.Model):
    name = models.CharField(max_length=30)
    name_j = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(max_length=30)
    region = models.ForeignKey(Region, on_delete=models.PROTECT)

    def __str__(self):
        return self.name


class Expansion(models.Model):
    name = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    pub_date = models.DateField(null=True)
    code = models.CharField(max_length=10)
    logo_url = models.CharField(max_length=2000, null=True)
    symbol_url = models.CharField(max_length=2000, null=True)
    info_url = models.CharField(max_length=2000)
    total_cards = models.IntegerField(null=True)
    series = models.CharField(max_length=20, null=True)

    def __str__(self):
        return self.name


class Regulation(models.Model):
    name = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=False)
    expansions = models.ManyToManyField(Expansion)

    def __str__(self):
        return self.name


class Rarity(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Series(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class PokemonRegion(models.Model):
    name = models.CharField(max_length=30)
    name_j = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class PokemonSpecies(models.Model):
    name = models.CharField(max_length=20)
    name_j = models.CharField(max_length=10)
#    form_name = models.CharField(max_length=20, default="")
    pokedex_number = models.IntegerField()
    region = models.ForeignKey(PokemonRegion, on_delete=models.PROTECT)
    evolves_from = models.ForeignKey('self', on_delete=models.PROTECT, null=True)

    def __str__(self):
        return self.name


class SuperType(models.Model):
    name = models.CharField(max_length=20)
    name_j = models.CharField(max_length=20, default="みてい")

    def __str__(self):
        return self.name


class SubType(models.Model):
    name = models.CharField(max_length=20)
    name_j = models.CharField(max_length=20, default="みてい")
    supertype = models.ForeignKey(SuperType, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Artist(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class CardName(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class CardText(models.Model):
    name = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class Card(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.PROTECT)
    set = models.ForeignKey(Expansion, on_delete=models.PROTECT)
    global_id_number = models.CharField(max_length=30)
    name = models.ForeignKey(CardName, on_delete=models.PROTECT)
    id_in_expansion = models.CharField(max_length=10, null=True)
    rarity = models.ForeignKey(Rarity, on_delete=models.PROTECT, null=True, default=None)
    is_prism_star = models.BooleanField(default=False)
    supertype = models.ForeignKey(SuperType, on_delete=models.PROTECT)
    subtype = models.ForeignKey(SubType, on_delete=models.PROTECT)
    text = models.ManyToManyField(CardText)
    image_url = models.CharField(max_length=200, null=True, default="")

    def __str__(self):
        return self.name.name


class Type(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Weakness(models.Model):
    name = models.CharField(max_length=50)
    type = models.ForeignKey(Type, on_delete=models.CASCADE)
    value = models.CharField(max_length=10)
    # e.g. "*2" "+30"

    def __str__(self):
        return self.name


class Resistance(models.Model):
    name = models.CharField(max_length=50)
    type = models.ForeignKey(Type, on_delete=models.CASCADE)
    value = models.CharField(max_length=10)
    # e.g. "*2" "+30"

    def __str__(self):
        return self.name


class Pokemon(Card):
    hp = models.IntegerField()
    retreat_cost = models.IntegerField()
    weakness = models.ForeignKey(Weakness, on_delete=models.PROTECT, null=True)
    resistance = models.ForeignKey(Resistance, on_delete=models.PROTECT, null=True)
    # species = models.ForeignKey(PokemonSpecies, on_delete=models.PROTECT)
    evolves_from = models.CharField(max_length=20, null=True, default=None)
    evolution_list_str = models.CharField(max_length=200)
    types = models.ManyToManyField(Type)


#
# class BasicPokemon(Pokemon):
#     pass
#
#
# class StageOnePokemon(Pokemon):
#     evolves_from = models.CharField(max_length=20)
#
#
# class StageTwoPokemon(Pokemon):
#     evolves_from = models.CharField(max_length=20)
#
#
# class BreakPokemon(Pokemon):
#     evolves_from = models.CharField(max_length=20)
#
#
# class EXPokemon(Pokemon):
#     text = models.CharField(max_length=50)
#
#
# class MegaEXPokemon(EXPokemon):
#     evolves_from = models.CharField(max_length=20)
#
#
# class GXBasicPokemon(BasicPokemon):
#     text = models.CharField(max_length=50)
#
#
# class GXStageOnePokemon(StageOnePokemon):
#     text = models.CharField(max_length=50)
#
#
# class GXStageTwoPokemon(StageTwoPokemon):
#     text = models.CharField(max_length=50)




# class Stadium(Trainers):
#     pass
#
#
# class Item(Trainers):
#     pass
#
#
# class Supporter(Trainers):
#     pass


class AbilityType(models.Model):
    name = models.CharField(max_length=50)
    name_j = models.CharField(max_length=50, default="みてい")

    def __str__(self):
        return self.name


class Ability(models.Model):
    name = models.CharField(max_length=50)
    text = models.CharField(max_length=500)
    type = models.ForeignKey(AbilityType, on_delete=models.PROTECT)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class AttackCost(models.Model):
    # nameは、','.join(cost_list)とすること。
    name = models.CharField(max_length=300)
    convertedEnergyCost = models.IntegerField(default=0)

    grass = models.IntegerField(default=0)
    fire = models.IntegerField(default=0)
    water = models.IntegerField(default=0)
    lightning = models.IntegerField(default=0)
    fighting = models.IntegerField(default=0)
    colorless = models.IntegerField(default=0)
    darkness = models.IntegerField(default=0)
    metal = models.IntegerField(default=0)
    fairly = models.IntegerField(default=0)
    free = models.IntegerField(default=0)

    dragon = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def get_list(self):
        return self.name.split(",")


class Attack(models.Model):
    name = models.CharField(max_length=30)
    damage = models.CharField(max_length=20)
    text = models.CharField(max_length=200)
    cost = models.ForeignKey(AttackCost, on_delete=models.PROTECT)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class ArchType(models.Model):
    name = models.CharField(max_length=100)
    regulation = models.ForeignKey(Regulation, on_delete=models.PROTECT)

    def __str__(self):
        return self.name


class Deck(models.Model):
    name = models.CharField(max_length=100)
    pub_date = models.DateTimeField()
    mod_date = models.DateTimeField()
    description = models.CharField(max_length=100000)
    owner = models.ForeignKey(PTCG2winUser, on_delete=models.PROTECT)
    regulation = models.ForeignKey(Regulation, on_delete=models.PROTECT)
    arch_type = models.ForeignKey(ArchType, on_delete=models.PROTECT)

    def __str__(self):
        return self.name


class DeckList(models.Model):
    parent_deck = models.ForeignKey(Deck, on_delete=models.CASCADE)
    deck_code = models.CharField(max_length=20, null=True)
    created_date = models.DateTimeField()

    def __str__(self):
        return self.deck_code


class CardBundle(models.Model):
    card = models.ForeignKey(Card, on_delete=models.PROTECT)
    amount = models.IntegerField(default=1)
    parent_deck_list = models.ForeignKey(DeckList, on_delete=models.CASCADE)

    def __str__(self):
        return self.card.name.name


class Topic(models.Model):
    name = models.CharField(max_length=150, default="Title is not set.")
    date = models.DateTimeField()

    def __str__(self):
        return self.name


class Comment(models.Model):
    date = models.DateTimeField()
    user = models.ForeignKey(PTCG2winUser, on_delete=models.PROTECT)
    text = models.CharField(max_length=10000, default="Comment text is not set.")

    def __str__(self):
        return self.text


class DeckTopic(Topic):
    parent_deck = models.ForeignKey(Deck, on_delete=models.CASCADE)


class DeckCode(models.Model):
    date = models.DateTimeField()
    text = models.CharField(max_length=24, default="Invalid deck code.")
    ip = models.CharField(max_length=20, default="0.0.0.0")

    def __str__(self):
        return self.text



from django.db import models


# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=30)
    login_id = models.CharField(max_length=30)

    def __str__(self):
        return self.name


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
    pub_date = models.DateField()
    code = models.CharField(max_length=10)
    logo_url = models.CharField(max_length=200)
    symbol_url = models.CharField(max_length=200)
    total_cards = models.IntegerField()
    series = models.CharField(max_length=20)

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
    name = models.CharField(max_length=20)

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


class Card(models.Model):
    artist = models.CharField(max_length=50)
    expansion = models.ForeignKey(Expansion, on_delete=models.PROTECT)  # setと対応
    global_id = models.CharField(max_length=30)
    name = models.CharField(max_length=100)
    name_j = models.CharField(max_length=100)
    id_in_expansion = models.CharField(max_length=10)
    rarity = models.ForeignKey(Rarity, on_delete=models.PROTECT)
    series = models.ForeignKey(Series, on_delete=models.PROTECT)
    is_prism_star = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Type(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Weakness(models.Model):
    name = models.CharField(max_length=50)
    type = models.ForeignKey(Type, on_delete=models.CASCADE)
    effect = models.CharField(max_length=10)  # e.g. "*2" "+30"

    def __str__(self):
        return self.name


class Pokemon(Card):
    hp = models.IntegerField()
    retreat_cost = models.IntegerField()
    weakness = models.ForeignKey(Weakness, on_delete=models.PROTECT)
    species = models.ForeignKey(PokemonSpecies, on_delete=models.PROTECT)


class BasicPokemon(Pokemon):
    pass


class StageOnePokemon(Pokemon):
    evolves_from = models.CharField(max_length=20)


class StageTwoPokemon(Pokemon):
    evolves_from = models.CharField(max_length=20)


class BreakPokemon(Pokemon):
    evolves_from = models.CharField(max_length=20)


class EXPokemon(Pokemon):
    text = models.CharField(max_length=50)


class MegaEXPokemon(EXPokemon):
    evolves_from = models.CharField(max_length=20)


class GXBasicPokemon(BasicPokemon):
    text = models.CharField(max_length=50)


class GXStageOnePokemon(StageOnePokemon):
    text = models.CharField(max_length=50)


class GXStageTwoPokemon(StageTwoPokemon):
    text = models.CharField(max_length=50)


class Trainers(Card):
    text = models.CharField(max_length=500)


class Stadium(Trainers):
    pass


class Item(Trainers):
    pass


class Supporter(Trainers):
    pass


class Ability(models.Model):
    name = models.CharField(max_length=50)
    text = models.CharField(max_length=500)
    pokemon = models.ForeignKey(Pokemon, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Attack(models.Model):
    name = models.CharField(max_length=30)
    damage = models.IntegerField(default=0)
    text = models.CharField(max_length=200)
    text_j = models.CharField(max_length=200)
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
    owner = models.ForeignKey(User, on_delete=models.PROTECT)
    regulation = models.ForeignKey(Regulation, on_delete=models.PROTECT)
    arch_type = models.ForeignKey(ArchType, on_delete=models.PROTECT)

    def __str__(self):
        return self.name


class CardBundle(models.Model):
    card = models.ForeignKey(Card, on_delete=models.PROTECT)
    amount = models.IntegerField(default=1)
    deck_list = models.ForeignKey(Deck, on_delete=models.CASCADE)

    def __str__(self):
        return self.card.name


class Comments(models.Model):
    name = models.CharField(max_length=150, default="Title is not set.")
    date = models.DateTimeField()

    def __str__(self):
        return self.name


class Comment(models.Model):
    date = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    text = models.CharField(max_length=10000, default="Comment text is not set.")

    def __str__(self):
        return self.text


class DeckComments(Comments):
    parent_deck = models.ForeignKey(Deck, on_delete=models.CASCADE)






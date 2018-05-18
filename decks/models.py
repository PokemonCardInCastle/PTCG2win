from django.db import models


# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=30)
    login_id = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Region(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(max_length=30)
    region = models.ForeignKey(Region, on_delete=models.PROTECT)

    def __str__(self):
        return self.name


class Expansion(models.Model):
    name = models.CharField(max_length=100)
    pub_date = models.DateField()

    def __str__(self):
        return self.name


class Regulation(models.Model):
    name = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=False)
    regulation_from = models.ForeignKey(Expansion, related_name="regulation_from", on_delete=models.PROTECT)
    regulation_to = models.ForeignKey(Expansion, related_name="regulation_to", on_delete=models.PROTECT)

    def __str__(self):
        return self.name


class Card(models.Model):
    expansion = models.ForeignKey(Expansion, on_delete=models.PROTECT)
    id_in_expansion = models.CharField(max_length=30)
    name = models.CharField(max_length=100)
    name_j = models.CharField(max_length=100)
    hp = models.IntegerField()

    def __str__(self):
        return self.name


class Move(models.Model):
    name = models.CharField(max_length=30)
    damage = models.IntegerField(default=0)
    text = models.CharField(max_length=200)
    text_j = models.CharField(max_length=200)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class ArchType(models.Model):
    name = models.CharField(max_length=100)
    expansion = models.ForeignKey(Regulation, models.PROTECT)

    def __str__(self):
        return self.name


class Deck(models.Model):
    name = models.CharField(max_length=100)
    pub_date = models.DateTimeField()
    mod_date = models.DateTimeField()
    description = models.CharField(max_length=100000)
    owner = models.ForeignKey(User, on_delete=models.PROTECT)
    arch_type = models.ForeignKey(ArchType, models.PROTECT)

    def __str__(self):
        return self.name


class DeckList(models.Model):
    parent_deck = models.ForeignKey(Deck, models.CASCADE)
    cards = models.ManyToManyField(Card, blank=True)  # "blank=True" is for temporary saving

    def __str__(self):
        return self.parent_deck


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






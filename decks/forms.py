from django import forms
from .models import *


class DeckRegisterForm(forms.ModelForm):

    class Meta:
        model = Deck
        fields = ("name", "description", "regulation", "arch_type", )
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "example: Reshiram GX Deck"}),
            "description": forms.Textarea(attrs={"rows": 5}),
            # "regulation": forms.ChoiceField(choices=[obj.name for obj in Regulation.objects.all()]),
            # "arch_type": forms.ChoiceField(choices=[arch_obj.name for arch_obj in ArchType.objects.all()]),
        }






from django import forms
from django.contrib.auth.forms import UserCreationForm
from accounts.models import PTCG2winUser

from django.db import models


class SignUpForm(UserCreationForm):
    email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())
    nick_name = models.CharField(max_length=30, blank=False)

    class Meta:
        model = PTCG2winUser
        fields = ('username', "nick_name", 'email', 'password1', 'password2')



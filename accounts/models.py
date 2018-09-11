from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class PTCG2winUser(User):
    nick_name = models.CharField(max_length=30, verbose_name="表示名")


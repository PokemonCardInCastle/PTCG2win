from django.urls import path

from . import views


app_name = 'decks'
urlpatterns = [
    # e.g. /decks/
    path("", views.signup, name="signup"),
]

from django.conf import settings
from django.db import models

# Create your models here.
from movie.models import Film


class Playlist(models.Model):
    name = models.CharField(max_length=25)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    film = models.ManyToManyField(Film, blank=True, null=True)

    def __str__(self):
        return f'{self.name}, Account: {self.user}'

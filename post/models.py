from django.db import models
from django.conf import settings
from movie.models import Film


class Post(models.Model):
    comment = models.TextField(max_length=250)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    film = models.ManyToManyField(Film)
    spoiler = models.BooleanField(default=False)

    def __str__(self):
        return f'Post by {self.user}, id: {self.pk}'

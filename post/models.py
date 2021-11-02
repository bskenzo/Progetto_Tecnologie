from django.db import models
from django.conf import settings
from movie.models import Film


class Post(models.Model):
    comment = models.TextField(max_length=250)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    film = models.ForeignKey(settings.AUTH_MOVIE_MODEL, on_delete=models.CASCADE)
    spoiler = models.BooleanField(default=False)

    def __str__(self):
        return f'Post by {self.user}, id: {self.pk}'


class Reply(models.Model):
    comment = models.TextField(max_length=250)
    spoiler = models.BooleanField(default=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    film = models.ForeignKey(settings.AUTH_MOVIE_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return f'Reply by {self.user}, id: {self.pk}'

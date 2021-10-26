from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from account.models import Account
from movienet import settings

CATEGORY_CHOICES = (
    ('action', 'Action'),
    ('drama', 'Drama'),
    ('comedy', 'Comedy'),
    ('romance', 'Romance'),
    ('horror', 'Horror'),
    ('noir', 'Noir'),
    ('western', 'Western'),
)


class Film(models.Model):
    title = models.CharField(max_length=20)
    genre = models.CharField(max_length=25, choices=CATEGORY_CHOICES)
    director = models.CharField(max_length=250)
    plot = models.TextField(max_length=250)
    poster = models.ImageField(upload_to='images/')
    release_date = models.DateField()
    date_posted = models.DateTimeField(auto_now_add=True, verbose_name="date published")
    price = models.CharField(max_length=250, default='7.99')
    video = models.FileField(upload_to="video/%y")

    def __str__(self):
        return self.title


class Review(models.Model):

    writer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    reviewed_film = models.ForeignKey(settings.AUTH_MOVIE_MODEL, related_name='reviews', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    rating = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])
    spoiler = models.BooleanField(default=False)
    date_posted = models.DateTimeField(auto_now_add=True, verbose_name="date published")

    def __str__(self):
        return f'{self.writer} -- {self.reviewed_film_id}'


class MyList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    film = models.ManyToManyField(Film)

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.timezone import now
from account.models import Account

# Create your models here.


class Film(models.Model):
    title = models.CharField(max_length=100)
    genre = models.CharField(max_length=250, default='N/a')
    director = models.CharField(max_length=250, default='N/a', null=True, blank=True)
    plot = models.TextField()
    poster = models.ImageField(default="default.png", upload_to="posters")
    release_date = models.DateField(blank=True, null=True)
    date_posted = models.DateTimeField(default=now)


class Review(models.Model):
    writer = models.ForeignKey(Account, on_delete=models.CASCADE)
    reviewed_film = models.ForeignKey(Film, related_name='reviews', on_delete=models.CASCADE)

    title = models.CharField(max_length=100)
    content = models.TextField()
    rating = models.IntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

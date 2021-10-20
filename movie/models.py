from django.db import models
from account.models import Account


class Film(models.Model):
    title = models.CharField(max_length=100)
    genre = models.CharField(max_length=250)
    director = models.CharField(max_length=250)
    plot = models.TextField(max_length=250)
    poster = models.ImageField(upload_to='images/')
    release_date = models.DateField()
    date_posted = models.DateTimeField(auto_now_add=True, verbose_name="date published")
    price = models.CharField(max_length=250, default='7.99')

    def __str__(self):
        return self.title

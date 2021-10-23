from django import forms

from account.models import Account
from movie.models import Film, Review


class FilmForm(forms.ModelForm):

    release_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}))

    class Meta:
        model = Film
        fields = [
            'title',
            'genre',
            'director',
            'plot',
            'poster',
            'release_date',
            'price',
        ]


class ReviewForm(forms.ModelForm):

    class Meta:
        model = Review
        fields = [
            'title',
            'content',
            'rating',
            'spoiler'
        ]

from django import forms

from movie.models import Film, Review


class FilmForm(forms.ModelForm):

    release_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}))
    price = forms.FloatField(widget=forms.NumberInput(attrs={'step': '0.01', 'value': '7.99', 'min': '0.5'}))

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
            'video'
        ]


class ReviewForm(forms.ModelForm):
    rating = forms.IntegerField(widget=forms.NumberInput(attrs={'min': '1', 'max': '5', 'value': '1'}))

    class Meta:
        model = Review
        fields = [
            'title',
            'content',
            'rating',
        ]

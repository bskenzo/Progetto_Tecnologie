from django import forms

from movie.models import Film


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


# class FilmUpdateForm(forms.ModelForm):
#
#     class Meta:
#         model = Film
#         fields = [
#             'title',
#             'genre',
#             'director',
#             'plot',
#             'poster',
#             'release_date',
#             'price',
#         ]

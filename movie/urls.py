from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path

from movie.views import FilmCreateView, FilmDetailView, FilmUpdateView, FilmDeleteView, MovieListView, CheckoutView, \
    MyListView, ReviewCreateView, ReviewUpdateView, ReviewDeleteView, FilmStreamView

app_name = 'movie'

urlpatterns = [
    path('create/',  staff_member_required(FilmCreateView.as_view()), name='create-view'),
    path('<int:pk>/detail', FilmDetailView.as_view(), name='film-detail'),
    path('<int:pk>/update', staff_member_required(FilmUpdateView.as_view()), name='update-film'),
    path('<int:pk>/delete', staff_member_required(FilmDeleteView.as_view()), name='delete-film'),
    path('<int:pk>/streaming', FilmStreamView.as_view(), name='stream-film'),
    path('list/', MovieListView.as_view(), name='list'),
    path('mylist/', MyListView.as_view(), name='my-list'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('<int:pk>/create-review/', ReviewCreateView.as_view(), name='create-review'),
    path('<int:pk>/update-review/', ReviewUpdateView.as_view(), name='update-review'),
    path('<int:pk>/delete-review/', ReviewDeleteView.as_view(), name='delete-review'),
]


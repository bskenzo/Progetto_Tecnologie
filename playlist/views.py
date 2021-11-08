from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages

# Create your views here.
from django.views.generic import TemplateView, CreateView

from movie.models import Film
from playlist.forms import PlaylistForm
from playlist.models import Playlist


class PlaylistView(LoginRequiredMixin, TemplateView, CreateView):
    model = Playlist
    template_name = 'playlist/playlist.html'
    form_class = PlaylistForm

    def get_context_data(self, **kwargs):
        context = {}
        playlists = Playlist.objects.filter(user_id=self.request.user.pk)
        context['playlists'] = playlists

        return context

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST['name']
            pl = Playlist()
            pl.name = name
            pl.user_id = request.user.pk
            pl.save()
        except:
            try:
                playlist = request.POST
                playlist = playlist['playlist']
                playlist = playlist.split('-')
                Playlist.objects.get(id=playlist[0]).delete()
            except:
                pass

        return redirect('playlist:playlist')


def add_to_playlist(request, operation, pk, playlist_id):
    playlist = Playlist.objects.get(pk=playlist_id)
    if playlist.user == request.user:
        new_film = Film.objects.get(pk=pk)
        if operation == 'add':
            messages.success(request, 'Film added to')
            playlist.film.add(new_film)
            return redirect('movie:film-detail', {'pk': pk})
        elif operation == 'remove':
            playlist.film.remove(new_film)
            messages.success(request, 'Film removed to')
            return redirect('playlist:playlist')
    else:
        messages.error(request, 'Selected Playlist does not exist')
        return redirect('home')

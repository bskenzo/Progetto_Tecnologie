from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib import messages

# Create your views here.
from django.views.generic import TemplateView

from movie.models import Film
from playlist.models import Playlist


class PlaylistView(LoginRequiredMixin, TemplateView):
    model = Playlist
    template_name = 'playlist/playlist.html'

    def get_context_data(self, **kwargs):
        context = {}
        playlists = Playlist.objects.all()
        context['playlists'] = playlists

        return context

    def get(self, request, *args, **kwargs):
        try:
            name = request.GET['name']
            pl = Playlist()
            pl.name = name
            pl.user_id = request.user.pk
            pl.save()
        except:
            pass

        return super(PlaylistView, self).get(request, *args, **kwargs)


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
        return redirect('movie:film-detail', {'pk': pk})

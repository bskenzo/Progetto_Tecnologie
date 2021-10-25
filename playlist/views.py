from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib import messages

# Create your views here.
from django.views.generic import CreateView, TemplateView

import playlist.models
from movie.models import Film
from playlist.forms import PlaylistForm
from playlist.models import Playlist


class PlaylistCreateView(LoginRequiredMixin, CreateView):
    model = Playlist
    template_name = 'playlist/playlist.html'

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account:must_authenticate')

        pl = playlist.models.Playlist()
        pl.name = request.POST.get('title')
        pl.user_id = request.user.pk
        pl.save()
        return render(request, 'playlist/playlist.html', {})


class PlaylistView(LoginRequiredMixin, TemplateView):
    model = Playlist
    template_name = 'playlist/playlist.html'

    def get_context_data(self, **kwargs):

        context = {}
        playlists = Playlist.objects.all()
        context['playlists'] = playlists

        return context


def add_to_playlist(request, operation, pk, playlist_id):
    context = {'pk': pk}
    playlist = Playlist.objects.get(pk=playlist_id)
    if playlist.user == request.user:
        new_film = Film.objects.get(pk=pk)
        if operation == 'add':
            messages.success(request, 'Film added to')
            playlist.film.add(new_film)
        elif operation == 'remove':
            playlist.film.remove(new_film)
            messages.success(request, 'Film removed to')
        return redirect('movie:film-detail', context['pk'])
    else:
        messages.error(request, 'Selected Playlist does not exist')
        return redirect('movie:film-detail', context['pk'])

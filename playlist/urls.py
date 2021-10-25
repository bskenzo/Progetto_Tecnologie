from django.urls import path

from playlist.views import add_to_playlist, PlaylistCreateView, PlaylistView

app_name = 'playlist'

urlpatterns = [
        path('<int:pk>/create', PlaylistCreateView.as_view(), name='create'),
        path('add_to_playlist/<int:playlist_id>/<str:operation>/<int:pk>', add_to_playlist, name='add-remove'),
        path('', PlaylistView.as_view(), name='playlist'),
    ]

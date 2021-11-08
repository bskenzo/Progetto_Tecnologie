from django.urls import path

from playlist.views import add_to_playlist, PlaylistView

app_name = 'playlist'

urlpatterns = [
        path('', PlaylistView.as_view(), name='playlist'),
        path('add_to_playlist/<int:playlist_id>/<str:operation>/<int:pk>', add_to_playlist, name='add-remove'),
]

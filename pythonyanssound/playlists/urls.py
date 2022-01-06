from django.urls import path

from playlists.views import (
    PlaylistListCreateView, PlaylistRetrieveUpdateDeleteView,
    LikedPlaylistsListView, ShortPlaylistListView, LikeUnlikePlaylistView,
    SongAddRemovePlaylistView
)

urlpatterns = [
    path(
        route='',
        view=PlaylistListCreateView.as_view(),
        name="own-playlists"),
    path(
        route='short/',
        view=ShortPlaylistListView.as_view(),
        name="short-playlists-list"
    ),
    path(
        route='<int:playlist_id>/',
        view=PlaylistRetrieveUpdateDeleteView.as_view(),
        name="playlist-management"
    ),
    path(
        route='songs/<int:playlist_id>/<int:song_id>/',
        view=SongAddRemovePlaylistView.as_view(),
        name="playlists-songs-management"
    ),
    path(
        route='likes/',
        view=LikedPlaylistsListView.as_view(),
        name="liked-playlists"
    ),
    path(
        route='likes/<int:playlist_id>/',
        view=LikeUnlikePlaylistView.as_view(),
        name="liked-playlists-management"
    ),
]

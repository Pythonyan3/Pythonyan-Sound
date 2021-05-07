from django.urls import path

from playlists.views import PlaylistListCreateView, PlaylistRetrieveUpdateDeleteView, LikedPlaylistsListView, \
    ShortPlaylistListView, LikeUnlikePlaylistView, SongAddRemovePlaylistView

urlpatterns = [
    path('', PlaylistListCreateView.as_view(), name="own-playlists"),
    path('short/', ShortPlaylistListView.as_view(), name="short-playlists-list"),
    path('<int:playlist_id>/', PlaylistRetrieveUpdateDeleteView.as_view(), name="playlist-management"),
    path('songs/<int:playlist_id>/<int:song_id>/', SongAddRemovePlaylistView.as_view(), name="playlists-songs-management"),
    path('likes/', LikedPlaylistsListView.as_view(), name="liked-playlists"),
    path('likes/<int:playlist_id>/', LikeUnlikePlaylistView.as_view(), name="liked-playlists-management"),
]

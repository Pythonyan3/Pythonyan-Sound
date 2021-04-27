from django.urls import path

from playlists.views import PlaylistListCreateView, PlaylistRetrieveUpdateDeleteView, LikesPlaylistsListView, \
    ShortPlaylistListView, LikePlaylistView, SongAddRemovePlaylistView

urlpatterns = [
    path('', PlaylistListCreateView.as_view()),
    path('short/', ShortPlaylistListView.as_view()),
    path('<int:playlist_id>/', PlaylistRetrieveUpdateDeleteView.as_view()),
    path('songs/<int:playlist_id>/<int:song_id>/', SongAddRemovePlaylistView.as_view()),
    path('likes/', LikesPlaylistsListView.as_view()),
    path('likes/<int:playlist_id>/', LikePlaylistView.as_view()),
]

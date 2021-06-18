from django.urls import path

from music.views import SongDetailsUpdateDeleteView, SongsListCreateView, LikedSongsListView, LikeSongView, \
    SongsNewReleasesView

urlpatterns = [
    path('', SongsListCreateView.as_view(), name="songs-list-create"),
    path('<int:song_id>/', SongDetailsUpdateDeleteView.as_view(), name="songs-detail-update-delete"),
    path('likes/', LikedSongsListView.as_view(), name="songs-likes"),
    path('likes/<int:song_id>/', LikeSongView.as_view(), name="songs-likes-management"),
    path('releases/', SongsNewReleasesView.as_view(), name="songs-releases"),
]

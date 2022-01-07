from django.urls import path

from music.views import (
    SongDetailsUpdateDeleteView, SongsListCreateView, LikedSongsListView,
    LikeSongView, SongsNewReleasesView
)

urlpatterns = [
    path(
        route='',
        view=SongsListCreateView.as_view(),
        name="songs-list-create"
    ),
    path(
        route='<int:song_id>/',
        view=SongDetailsUpdateDeleteView.as_view(),
        name="songs-detail-update-delete"
    ),
    path(
        route='likes/',
        view=LikedSongsListView.as_view(),
        name="songs-likes"
    ),
    path(
        route='likes/<int:song_id>/',
        view=LikeSongView.as_view(),
        name="songs-likes-management"
    ),
    path(
        route='releases/',
        view=SongsNewReleasesView.as_view(),
        name="songs-releases"
    ),
]

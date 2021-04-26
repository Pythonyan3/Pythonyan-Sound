from django.urls import path

from music.views import SongDetailsUpdateDeleteView, SongsListCreateView, LikedSongsListView, LikeSongView

urlpatterns = [
    path('', SongsListCreateView.as_view()),
    path('<int:song_id>/', SongDetailsUpdateDeleteView.as_view()),
    path('likes/', LikedSongsListView.as_view()),
    path('likes/<int:song_id>/', LikeSongView.as_view()),
]

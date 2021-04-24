from django.urls import path

from music.views import SongDetailsUpdateDeleteView, SongsListCreateView

urlpatterns = [
    path('', SongsListCreateView.as_view()),
    path('<int:song_id>/', SongDetailsUpdateDeleteView.as_view()),
]

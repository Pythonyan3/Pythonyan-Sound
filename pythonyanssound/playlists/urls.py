from django.urls import path

from playlists.views import PlaylistListCreateView, PlaylistRetrieveUpdateDeleteView

urlpatterns = [
    path('', PlaylistListCreateView.as_view()),
    path('<int:playlist_id>/', PlaylistRetrieveUpdateDeleteView.as_view())
]

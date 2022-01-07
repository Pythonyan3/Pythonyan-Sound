from django.urls import path

from search.views import (
    SearchListView, ArtistsSearchView, ProfilesSearchView,
    PlaylistsSearchView, SongsSearchView
)


urlpatterns = [
    path(
        route="<str:search_string>/",
        view=SearchListView.as_view(),
        name="search"
    ),
    path(
        route="artist/<str:search_string>/",
        view=ArtistsSearchView.as_view(),
        name="search-artist"
    ),
    path(
        route="profile/<str:search_string>/",
        view=ProfilesSearchView.as_view(),
        name="search-profile"
    ),
    path(
        route="playlist/<str:search_string>/",
        view=PlaylistsSearchView.as_view(),
        name="search-playlist"
    ),
    path(
        route="song/<str:search_string>/",
        view=SongsSearchView.as_view(),
        name="search-song"
    ),
]

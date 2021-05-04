from django.urls import path

from search.views import SearchListView, ArtistsSearchView, ProfilesSearchView, PlaylistsSearchView, SongsSearchView

urlpatterns = [
    path("<str:search_string>/", SearchListView.as_view(), name="search"),
    path("artist/<str:search_string>/", ArtistsSearchView.as_view(), name="search-artist"),
    path("profile/<str:search_string>/", ProfilesSearchView.as_view(), name="search-profile"),
    path("playlist/<str:search_string>/", PlaylistsSearchView.as_view(), name="search-playlist"),
    path("song/<str:search_string>/", SongsSearchView.as_view(), name="search-song"),
]

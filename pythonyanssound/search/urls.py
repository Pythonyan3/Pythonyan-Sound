from django.urls import path

from search.views import SearchListView, ArtistsSearchView, ProfilesSearchView, PlaylistsSearchView, SongsSearchView

urlpatterns = [
    path("<str:search_string>/", SearchListView.as_view()),
    path("artist/<str:search_string>/", ArtistsSearchView.as_view()),
    path("profile/<str:search_string>/", ProfilesSearchView.as_view()),
    path("playlist/<str:search_string>/", PlaylistsSearchView.as_view()),
    path("song/<str:search_string>/", SongsSearchView.as_view()),
]

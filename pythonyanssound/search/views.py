from django.db.models import Count
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from music.models import Song
from music.serializers import SearchSongSerializer
from playlists.models import Playlist
from playlists.serializers import SearchPlaylistSerializer
from profiles.models import Profile
from profiles.serializers import SearchProfileSerializer
from pythonyanssound.pagination import CustomPageNumberPagination


class SearchListView(APIView):
    """
    Processes GET method to obtain search data
    Allowed only to authenticated users
    """
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, search_string: str):
        """
        Returns JSON with corresponds Profiles, Playlists, Songs
        Performs case insensitive filter by main fields of instances
        (song - title, playlist - title, profile - username)
        Also divides artist users and non artist users ordered by popularity (followers count)
        """
        # python's slices works like SQL LIMIT
        artists = Profile.objects.annotate(followers_count=Count("followers")).\
            filter(username__icontains=search_string, is_artist=True).order_by('-followers_count')[:10]
        profiles = Profile.objects.annotate(followers_count=Count("followers")). \
            filter(username__icontains=search_string, is_artist=False).order_by('-followers_count')[:10]
        playlists = Playlist.objects.filter(title__icontains=search_string)[:10]
        songs = Song.objects.filter(title__icontains=search_string)[:10]

        artists_serializer = SearchProfileSerializer(instance=artists, many=True)
        profile_serializer = SearchProfileSerializer(instance=profiles, many=True)
        playlist_serializer = SearchPlaylistSerializer(instance=playlists, many=True)
        song_serializer = SearchSongSerializer(instance=songs, many=True)

        return Response(data={
            "artists": artists_serializer.data,
            "profiles": profile_serializer.data,
            "playlists": playlist_serializer.data,
            "songs": song_serializer.data
        })


class ArtistsSearchView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SearchProfileSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        return Profile.objects.annotate(followers_count=Count("followers")).\
            filter(username__icontains=self.kwargs.get("search_string"), is_artist=True).order_by('-followers_count')


class ProfilesSearchView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SearchProfileSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        return Profile.objects.annotate(followers_count=Count("followers")). \
            filter(username__icontains=self.kwargs.get("search_string"), is_artist=False).order_by('-followers_count')


class PlaylistsSearchView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SearchPlaylistSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        return Playlist.objects.filter(title__icontains=self.kwargs.get("search_string")).order_by("title")


class SongsSearchView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SearchSongSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        return Song.objects.filter(title__icontains=self.kwargs.get("search_string")).order_by("title")
